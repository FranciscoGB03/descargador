#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de reproducción de medios usando ffplay - Linux/Windows
Versión COMPATIBLE: Sin flags problemáticos para video
"""

import subprocess
import os
import threading
import time
from typing import List, Callable, Optional
from core.utils import get_ffplay_path, get_base_dir, is_linux
import signal


class PlayerEngine:
    def __init__(self, base_dir: Optional[str] = None, callback: Callable[[str], None] = None):
        self.base_dir = base_dir or get_base_dir()
        self.callback = callback or (lambda e: None)
        self.playlist: List[str] = []
        self.current_index = -1
        self.is_playing = False
        self._process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
        self._start_time: Optional[float] = None
        self._current_file: Optional[str] = None
        self._lock = threading.Lock()
        self._is_loading_flag = False

    def play_file(self, file_path: str, volume: int = 100, skip_loading_check: bool = False):
        """
        Reproduce un archivo con ffplay.
        skip_loading_check: si True, ignora _is_loading (para next/prev)
        """
        # Solo bloquear si no es una navegación forzada
        if not skip_loading_check:
            with self._lock:
                if self._is_loading_flag:
                    print(f"⏳ Ya está cargando, ignorando {file_path}")
                    return
                self._is_loading_flag = True
        
        self._current_file = file_path
        print(f"🎵 Reproduciendo: {os.path.basename(file_path)} (Índice: {self.current_index})")

        # CRÍTICO: Limpiar proceso anterior ANTES de iniciar el nuevo
        self._cleanup_process()
        
        ffplay_path = get_ffplay_path(self.base_dir)
        is_audio = file_path.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.opus'))

        # Comando base - SIN FLAGS PROBLEMÁTICOS
        cmd = [ffplay_path, "-i", file_path, "-autoexit", "-window_title", os.path.basename(file_path)]
        
        # Filtro de volumen
        if volume != 100:
            volume_filter = f"volume={volume/100.0}"
            cmd.extend(['-af', volume_filter])
        
        # Solo -nodisp para audio (para video dejar que ffplay decida)
        if is_audio:
            cmd.append("-nodisp")

        try:
            # Sin start_new_session para mantener conexión con display en Linux
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,  # ← CAMBIO: Capturar stderr para ver errores
            )
            self._start_time = time.time()
            self.is_playing = True
            self.callback("playing")

            self._stop_event.clear()
            t = threading.Thread(target=self._monitor_process, daemon=True, args=(file_path,))
            t.start()
            
        except Exception as e:
            if not skip_loading_check:
                self._is_loading_flag = False
            print(f"❌ Error al iniciar ffplay: {e}")
            self.callback(f"error: {str(e)}")

    def _monitor_process(self, expected_file: str):
        """Monitorea el proceso ffplay y captura errores"""
        if self._process:
            try:
                # Leer stderr mientras espera
                stderr_output = []
                
                def read_stderr():
                    try:
                        for line in iter(self._process.stderr.readline, b''):
                            stderr_output.append(line.decode('utf-8', errors='ignore'))
                    except:
                        pass
                
                # Leer stderr en thread separado
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stderr_thread.start()
                
                # Esperar a que termine
                return_code = self._process.wait()
                duration = time.time() - self._start_time if self._start_time else 0
                
                # Cerrar stderr
                if self._process.stderr:
                    self._process.stderr.close()
                
                # Verificar que no fue cancelado manualmente
                if self._stop_event.is_set():
                    print(f"⏹ Reproducción cancelada por usuario")
                    if not hasattr(self, '_skip_loading_on_finish'):
                        self._is_loading_flag = False
                    return
                
                # Mostrar stderr si hay error
                if return_code != 0 or duration < 1.0:
                    print(f"⚠️ Error en reproducción:")
                    print(f"   Duración: {duration:.2f}s")
                    print(f"   Código: {return_code}")
                    if stderr_output:
                        print(f"   Error de ffplay:")
                        for line in stderr_output[-5:]:  # Últimas 5 líneas
                            print(f"     {line.strip()}")
                    self.callback("error_ffplay")
                    if not hasattr(self, '_skip_loading_on_finish'):
                        self._is_loading_flag = False
                    return
                
                print(f"✅ Canción terminada: {os.path.basename(expected_file)} (duración: {duration:.1f}s)")
                
            except Exception as e:
                print(f"⚠️ Error monitoreando: {e}")
                if not hasattr(self, '_skip_loading_on_finish'):
                    self._is_loading_flag = False
                return
            
            # Solo avanzar si hay más canciones y NO se detuvo manualmente
            if not self._stop_event.is_set() and self.is_playing:
                print(f"🔄 Avanzando a siguiente pista...")
                self.callback("finished")
                if len(self.playlist) > 1:
                    self.next_track()
            else:
                print(f"🛑 No se avanza: stop_event={self._stop_event.is_set()}, is_playing={self.is_playing}")
                    
        if not hasattr(self, '_skip_loading_on_finish'):
            self._is_loading_flag = False

    def _cleanup_process(self):
        """Detiene el proceso ffplay"""
        print(f"🧹 Limpiando proceso...")
        self._stop_event.set()
        self.is_playing = False
        
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                try:
                    self._process.wait(timeout=2)
                    print("✅ Proceso terminado con SIGTERM")
                except subprocess.TimeoutExpired:
                    print("⚠️ Timeout en SIGTERM, usando SIGKILL")
                    self._process.kill()
                    self._process.wait(timeout=1)
            except ProcessLookupError:
                print("ℹ️ Proceso ya había terminado")
            except Exception as e:
                print(f"⚠️ Error limpiando proceso: {e}")
            finally:
                self._process = None
        else:
            print("ℹ️ No había proceso activo")

    def stop(self):
        """Detiene la reproducción actual"""
        print("⏹ Stop manual")
        self._cleanup_process()
        self._is_loading_flag = False

    def next_track(self):
        """Avanza a la siguiente pista - NAVEGACIÓN FORZADA"""
        if not self.playlist:
            print("⚠️ No hay playlist")
            return
            
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.playlist)
        print(f"⏭ Next: {old_index} → {self.current_index} de {len(self.playlist)}")
        
        # Flag temporal para evitar que el monitor resetee _is_loading_flag
        self._skip_loading_on_finish = True
        
        # Reproducir inmediatamente la siguiente (ignorando _is_loading)
        next_file = self.playlist[self.current_index]
        self.play_file(next_file, skip_loading_check=True)
        
        # Limpiar flag después de iniciar
        if hasattr(self, '_skip_loading_on_finish'):
            delattr(self, '_skip_loading_on_finish')

    def prev_track(self):
        """Retrocede a la pista anterior - NAVEGACIÓN FORZADA"""
        if not self.playlist:
            print("⚠️ No hay playlist")
            return
            
        old_index = self.current_index
        self.current_index = (self.current_index - 1) % len(self.playlist)
        print(f"⏮ Prev: {old_index} → {self.current_index} de {len(self.playlist)}")
        
        # Flag temporal
        self._skip_loading_on_finish = True
        
        # Reproducir inmediatamente la anterior
        prev_file = self.playlist[self.current_index]
        self.play_file(prev_file, skip_loading_check=True)
        
        # Limpiar flag
        if hasattr(self, '_skip_loading_on_finish'):
            delattr(self, '_skip_loading_on_finish')

    def pause(self):
        """Pausa o reanuda la reproducción"""
        if self._process and self._process.poll() is None:
            if is_linux():
                # En Linux, enviar SIGSTOP/SIGCONT
                if self.is_playing:
                    print("⏸ Pausando (SIGSTOP)")
                    self._process.send_signal(signal.SIGSTOP)
                    self.is_playing = False
                else:
                    print("▶️ Reanudando (SIGCONT)")
                    self._process.send_signal(signal.SIGCONT)
                    self.is_playing = True
            else:
                # En Windows, no hay forma nativa de pausar, así que solo toggle el estado
                print("⚠️ Pausa no soportada en Windows, toggle estado")
                self.is_playing = not self.is_playing
        else:
            print("⚠️ No hay proceso activo para pausar/reanudar")