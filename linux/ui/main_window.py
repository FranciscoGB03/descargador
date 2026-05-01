#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal de la aplicación - UI con CustomTkinter
Compatible con Windows y Linux
Mejoras: Reproducir Todo + Control de Volumen + Persistencia de Carpetas
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.filedialog as filedialog
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

# Importar módulos del proyecto
from core.downloader import YouTubeDownloader
from core.player import PlayerEngine
from core.utils import get_base_dir, get_ffmpeg_path, is_linux
from core.tooltip import ToolTip

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader & Player")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # Configuración de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Detectar directorio base correctamente
        self.base_dir = get_base_dir()
        self.ffmpeg_path = get_ffmpeg_path(self.base_dir)
        
        # Configuración y persistencia
        self.config_file = Path.home() / ".config" / "youtube_downloader_config.json"
        self.saved_config = self._load_config()
        self.current_folder = self.saved_config.get('last_folder', '')
        
        # Variable para control de volumen
        self.volume_var = ctk.IntVar(value=self.saved_config.get('volume', 100))

        # Inicializar componentes
        try:
            self.downloader = YouTubeDownloader(self._handle_download_callback, self.base_dir)
            self.player = PlayerEngine(self.base_dir, self._handle_player_callback)
        except Exception as e:
            print(f"⚠️ Error cargando módulos: {e}")

        self._setup_ui()
        
        # Ajustes específicos para Linux
        if is_linux():
            self._apply_linux_fixes()
        
        # Cargar biblioteca si hay carpeta guardada
        if self.current_folder:
            self.after(200, lambda: self._auto_load_library())

    def _auto_load_library(self):
        """Carga la biblioteca automáticamente si hay carpeta configurada"""
        if self.current_folder and os.path.isdir(self.current_folder):
            self._update_folder_entries(self.current_folder)
            self._refresh_library()

    def _apply_linux_fixes(self):
        """Ajustes específicos para mejorar experiencia en Linux"""
        self.after(100, lambda: ctk.set_appearance_mode("dark"))

    def _safe_ui_update(self, callback):
        """Ejecuta callback en el hilo principal de forma segura"""
        if not self.winfo_exists():
            return
        try:
            self.after(0, lambda: self._execute_safe(callback))
        except tk.TclError:
            pass

    def _execute_safe(self, callback):
        """Ejecuta callback con protección extra contra widgets destruidos"""
        try:
            if self.winfo_exists():
                callback()
        except tk.TclError:
            pass

    # ═══════════════════════════════════════════════════════════
    # 📁 GESTIÓN DE CONFIGURACIÓN (Persistencia)
    # ═══════════════════════════════════════════════════════════
    
    def _load_config(self) -> dict:
        """Carga configuración desde archivo JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando config: {e}")
        return {'last_folder': '', 'download_folder': '', 'volume': 100}

    def _save_config(self, key: str, value):
        """Guarda configuración en archivo JSON"""
        config = self._load_config()
        config[key] = value
        
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error guardando config: {e}")

    def _update_folder_entries(self, folder: str):
        """Actualiza ambos campos de carpeta (descarga y biblioteca)"""
        if hasattr(self, 'folder_entry') and self.folder_entry.winfo_exists():
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="readonly")
            
        if hasattr(self, 'lib_folder_entry') and self.lib_folder_entry.winfo_exists():
            self.lib_folder_entry.configure(state="normal")
            self.lib_folder_entry.delete(0, "end")
            self.lib_folder_entry.insert(0, folder)
            self.lib_folder_entry.configure(state="readonly")

    # ═══════════════════════════════════════════════════════════
    # 🔊 CONTROL DE VOLUMEN
    # ═══════════════════════════════════════════════════════════
    
    def _change_volume(self, value=None):
        """Cambia el volumen del sistema (Linux: PulseAudio/PipeWire, Windows: nircmd)"""
        try:
            volume = int(self.volume_var.get())
            
            if is_linux():
                # Intentar con pactl (PulseAudio/PipeWire)
                result = subprocess.run(
                    ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'],
                    capture_output=True, text=True, timeout=2
                )
                # Si falla pactl, intentar con amixer (ALSA)
                if result.returncode != 0:
                    subprocess.run(
                        ['amixer', 'sset', 'Master', f'{volume}%'],
                        capture_output=True, timeout=2
                    )
            else:
                # Windows: opcionalmente usar pycaw o nircmd
                # Por ahora, solo actualizar UI
                pass
                
            # Guardar preferencia
            self._save_config('volume', volume)
            
            # Feedback visual
            icon = "🔇" if volume == 0 else "🔈" if volume < 40 else "🔉" if volume < 80 else "🔊"
            if self.winfo_exists():
                self.status_label.configure(text=f"{icon} Volumen: {volume}%", text_color="#3498DB")
                
        except Exception as e:
            print(f"⚠️ No se pudo cambiar volumen: {e}")

    # ═══════════════════════════════════════════════════════════
    # 🎵 SETUP DE INTERFAZ
    # ═══════════════════════════════════════════════════════════
    
    def _setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self, width=680, height=580, corner_radius=15)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabview.add("⬇️ Descargar")
        self.tabview.add("🎧 Biblioteca")

        self._setup_download_tab()
        self._setup_library_tab()

    def _setup_download_tab(self):
        tab = self.tabview.tab("⬇️ Descargar")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="URL del Video / Playlist:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="w", pady=(15, 5), padx=20)
        
        self.url_entry = ctk.CTkEntry(tab, placeholder_text="https://www.youtube.com/...", height=35)
        self.url_entry.grid(row=1, column=0, pady=(0, 15), sticky="ew", padx=20)

        ctk.CTkLabel(tab, text="Carpeta de destino:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", pady=(0, 5), padx=20)
        
        folder_frame = ctk.CTkFrame(tab, fg_color="transparent")
        folder_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15), padx=20)
        
        self.folder_entry = ctk.CTkEntry(folder_frame, placeholder_text="Selecciona carpeta...", state="readonly", height=35)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(folder_frame, text="📁", width=45, height=35, command=self._browse_folder).pack(side="right", padx=(10, 0))

        opts_frame = ctk.CTkFrame(tab, corner_radius=10, fg_color="#1A1A1A")
        opts_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15), padx=20)

        ctk.CTkLabel(opts_frame, text="Formato:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(15, 10), pady=10, sticky="w")
        self.fmt_var = ctk.StringVar(value="mp4")
        for i, txt in enumerate(["MP4", "MP3", "MKV"]):
            ctk.CTkRadioButton(opts_frame, text=txt, variable=self.fmt_var, value=txt.lower(), width=80).grid(
                row=0, column=i+1, padx=10, pady=10)

        ctk.CTkLabel(opts_frame, text="Modo:", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts_frame, text="Descargar playlist completa", variable=self.playlist_var, command=self._toggle_items).grid(
            row=1, column=1, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkLabel(opts_frame, text="Rangos (ej: 1,3-5):", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
        self.items_entry = ctk.CTkEntry(opts_frame, placeholder_text="Opcional", state="disabled", height=30, width=200)
        self.items_entry.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="w")

        self.download_btn = ctk.CTkButton(tab, text="⬇️ Descargar", height=45, font=ctk.CTkFont(size=18, weight="bold"), command=self._start_download)
        self.download_btn.grid(row=5, column=0, pady=(10, 15), sticky="ew", padx=20)

        self.progress_bar = ctk.CTkProgressBar(tab, height=12, corner_radius=6)
        self.progress_bar.grid(row=6, column=0, sticky="ew", pady=(0, 10), padx=20)
        self.progress_bar.set(0)

        self.dl_status = ctk.CTkLabel(tab, text="Listo para descargar", text_color="#8A8A8A", font=ctk.CTkFont(size=13))
        self.dl_status.grid(row=7, column=0, pady=(0, 20))

    def _setup_library_tab(self):
        tab = self.tabview.tab("🎧 Biblioteca")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(15, 10), padx=15)
        
        self.lib_folder_entry = ctk.CTkEntry(top_frame, placeholder_text="Selecciona carpeta...", state="readonly", height=35)
        self.lib_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(top_frame, text="📂", width=45, command=self._browse_lib_folder).pack(side="right")

        list_frame = ctk.CTkFrame(tab, fg_color="#1A1A1A", corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(list_frame, text="📂 Archivos", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, pady=10)
        
        self.playlist_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent", scrollbar_button_color="#555")
        self.playlist_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # === Botonera de controles ===
        btn_frame = ctk.CTkFrame(tab, fg_color="#1A1A1A", height=80, corner_radius=12)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        btn_frame.pack_propagate(False)

        # Botones de navegación
        btn_prev=ctk.CTkButton(btn_frame, text="⏮", width=50, command=self._prev_track)
        btn_prev.pack(side="left", padx=(15, 5), pady=10)
        ToolTip(btn_prev, "Pista anterior", delay=0.3)
        btn_stop=ctk.CTkButton(btn_frame, text="⏹", width=50, fg_color="#E74C3C", hover_color="#C0392B", command=self._stop_playback)
        btn_stop.pack(side="left", padx=5, pady=10)
        ToolTip(btn_stop, "Detener reproducción", delay=0.3)
        btn_pause=ctk.CTkButton(btn_frame, text="⏯", width=50, fg_color="#3498DB", hover_color="#2980B9", command=self._pause_playback)
        btn_pause.pack(side="left", padx=5, pady=10)
        ToolTip(btn_pause, "Pausar/Reanudar", delay=0.3)
        btn_next=ctk.CTkButton(btn_frame, text="⏭", width=50, command=self._next_track)
        btn_next.pack(side="left", padx=5, pady=10)
        ToolTip(btn_next, "Siguiente pista", delay=0.3)
        
        # 🎵 NUEVO: Botón Reproducir Todo
        ctk.CTkButton(
            btn_frame, 
            text="▶️ Todo", 
            width=90,
            fg_color="#27AE60",
            hover_color="#229954",
            command=self._play_all_tracks
        ).pack(side="left", padx=(15, 5), pady=10)
        
        # 🔊 NUEVO: Control de volumen
        volume_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        volume_frame.pack(side="right", padx=15, pady=10)
        
        ctk.CTkLabel(volume_frame, text="🔊", font=ctk.CTkFont(size=12)).pack(side="top")
        
        volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            variable=self.volume_var,
            command=lambda v: self._change_volume(),
            width=120
        )
        volume_slider.pack(side="bottom", pady=(5, 0))
        volume_slider.set(self.volume_var.get())

        # Label de estado
        self.status_label = ctk.CTkLabel(btn_frame, text="Selecciona una carpeta", text_color="#888", font=ctk.CTkFont(size=14))
        self.status_label.pack(side="right", padx=20)

    # ═══════════════════════════════════════════════════════════
    # 🎬 MÉTODOS DE ACCIÓN
    # ═══════════════════════════════════════════════════════════
    
    def _browse_folder(self):
        """Selector de carpeta para descargas (sincroniza con biblioteca)"""
        initial = self.current_folder or os.path.expanduser("~")
        folder = filedialog.askdirectory(initialdir=initial)
        if folder:
            self.current_folder = folder
            self._update_folder_entries(folder)
            self._save_config('last_folder', folder)
            self._save_config('download_folder', folder)
            self._refresh_library()

    def _browse_lib_folder(self):
        """Selector de carpeta para biblioteca"""
        initial = self.current_folder or os.path.expanduser("~")
        folder = filedialog.askdirectory(initialdir=initial)
        if folder:
            self.current_folder = folder
            self._update_folder_entries(folder)
            self._save_config('last_folder', folder)
            self._refresh_library()

    def _toggle_items(self):
        """Habilita/deshabilita campo de rangos para playlists"""
        state = "normal" if self.playlist_var.get() else "disabled"
        self.items_entry.configure(state=state)

    def _start_download(self):
        """Inicia la descarga con validaciones"""
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip() or os.path.join(os.path.expanduser("~"), "Downloads")
        
        if not url:
            self._safe_ui_update(lambda: self.dl_status.configure(text="Ingresa una URL válida", text_color="#E74C3C"))
            return

        self.download_btn.configure(state="disabled", text="⏳ Procesando...")
        self.progress_bar.set(0)
        self._safe_ui_update(lambda: self.dl_status.configure(text="Conectando...", text_color="#4A90E2"))

        self.downloader.start_download(
            url=url, 
            fmt=self.fmt_var.get(), 
            output_dir=folder,
            is_playlist=self.playlist_var.get(),
            items=self.items_entry.get().strip() if self.playlist_var.get() else None
        )

    def _play_all_tracks(self):
        """🎵 NUEVO: Reproduce toda la playlist desde el inicio"""
        if not hasattr(self, 'player') or not self.player.playlist:
            self.status_label.configure(text="No hay archivos para reproducir", text_color="#E74C3C")
            return
        
        self.player.current_index = -1  # Reiniciar al inicio
        self.player.next_track()  # Esto cargará y reproducirá el primer archivo
        self.status_label.configure(text="▶️ Reproduciendo playlist completa", text_color="#2ECC71")

    # ═══════════════════════════════════════════════════════════
    # 🔄 CALLBACKS Y ACTUALIZACIONES
    # ═══════════════════════════════════════════════════════════
    
    def _handle_download_callback(self, event: str, data):
        """Callback del downloader con protección contra race conditions"""
        
        def safe_update(func):
            """Wrapper seguro para actualizaciones de UI"""
            if not self.winfo_exists():
                print(f"⚠️ safe_update: UI no existe, ignorando {event}")
                return
            try:
                self.after(0, lambda: self._execute_safe(func))
            except tk.TclError as e:
                print(f"⚠️ safe_update: TclError en {event}: {e}")
        
        if event == "start":
            print(f" Descarga iniciada")
            safe_update(lambda: self.dl_status.configure(text=data, text_color="#4A90E2"))
            
        elif event == "progress":
            pct, speed = data
            safe_update(lambda: self.progress_bar.set(pct))
            safe_update(lambda: self.dl_status.configure(
                text=f"⚡ {speed} | {int(pct*100)}%", text_color="#B0B0B0"))
            
        elif event == "finished":
            print(f"✅ Descarga completada")
            safe_update(lambda: self.dl_status.configure(text="¡Listo!", text_color="#2ECC71"))
            safe_update(lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))
            safe_update(lambda: self.progress_bar.set(1.0))
            
            # Esperar un momento antes de refrescar biblioteca
            # Esto evita race conditions con la UI
            def delayed_refresh():
                if self.winfo_exists():
                    current_dl_folder = self.folder_entry.get().strip()
                    if self.current_folder and current_dl_folder in self.current_folder:
                        print(f"🔄 Refrescando biblioteca...")
                        self._refresh_library()
                    else:
                        print(f"ℹ️  No se refresca: current_folder={self.current_folder}, dl_folder={current_dl_folder}")
                else:
                    print(f"⚠️ delayed_refresh: UI no existe")
            
            # Esperar 500ms para que la UI termine de actualizarse
            self.after(500, delayed_refresh)
            
        elif event == "error":
            print(f"❌ Error en descarga: {data}")
            safe_update(lambda: self.dl_status.configure(text=str(data), text_color="#E74C3C"))
            safe_update(lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))

    def _refresh_library(self):
        """Refresca la lista de archivos con protecciones máximas"""
        if not self.current_folder or not self.winfo_exists():
            print("⚠️ _refresh_library: UI no existe o no hay carpeta")
            return

        try:
            # Verificar elementos críticos
            if not hasattr(self, 'playlist_scroll') or not self.playlist_scroll.winfo_exists():
                print("⚠️ _refresh_library: playlist_scroll no existe")
                return

            # Limpiar lista anterior CON protecciones
            children = self.playlist_scroll.winfo_children()
            print(f"🧹 Limpiando {len(children)} botones anteriores...")
            
            for w in children:
                try:
                    if w.winfo_exists():
                        # Desconectar comandos antes de destruir
                        if hasattr(w, 'configure'):
                            try:
                                w.configure(command=None)
                            except:
                                pass
                        w.destroy()
                except tk.TclError:
                    pass  # Widget ya destruido

            # Escanear archivos
            supported = ('.mp3', '.mp4', '.mkv', '.webm', '.m4a', '.flac', '.wav', '.opus')
            try:
                files = sorted([
                    os.path.join(self.current_folder, f) for f in os.listdir(self.current_folder)
                    if f.lower().endswith(supported) and os.path.isfile(os.path.join(self.current_folder, f))
                ])
            except Exception as e:
                print(f"⚠️ Error escaneando carpeta: {e}")
                files = []

            if not files:
                if self.playlist_scroll.winfo_exists():
                    ctk.CTkLabel(self.playlist_scroll, text="No hay archivos multimedia", text_color="#666").pack(pady=20)
                if self.winfo_exists():
                    self.status_label.configure(text="Carpeta vacía", text_color="#888")
                return

            print(f"✅ Encontrados {len(files)} archivos")

            # Actualizar player
            if hasattr(self, 'player'):
                self.player.playlist = files
                self.player.current_index = -1  # ← ¡IMPORTANTE! Resetear índice

            # Crear nuevos botones CON verificación
            for idx, fpath in enumerate(files):
                if not self.playlist_scroll.winfo_exists():
                    print(f"⚠️ playlist_scroll destruido en índice {idx}")
                    break
                    
                fname = os.path.basename(fpath)
                
                # Crear botón con closure seguro
                def make_command(path):
                    return lambda: self._play_from_list(path)
                
                try:
                    btn = ctk.CTkButton(
                        self.playlist_scroll, 
                        text=f"🎵 {fname}", 
                        anchor="w", 
                        height=40,
                        command=make_command(fpath)
                    )
                    btn.pack(fill="x", pady=2, padx=5)
                except Exception as e:
                    print(f"⚠️ Error creando botón {idx}: {e}")
                    break
            
            # Actualizar estado
            if self.winfo_exists():
                self.status_label.configure(text=f"{len(files)} archivos listos", text_color="#888")
                print(f"✅ Biblioteca actualizada: {len(files)} archivos")
                    
        except tk.TclError as e:
            print(f"⚠️ TclError en _refresh_library: {e}")
            # UI ya fue destruida, salir silenciosamente
        except Exception as e:
            print(f"❌ Error en _refresh_library: {e}")
            import traceback
            traceback.print_exc()

    def _play_from_list(self, file_path):
        """Reproduce un archivo específico con verificaciones"""
        if not self.winfo_exists():
            print(f"⚠️ _play_from_list: UI no existe")
            return
        
        if not hasattr(self, 'player'):
            print(f"❌ _play_from_list: player no existe")
            return
        
        try:
            # Encontrar el índice del archivo
            if hasattr(self.player, 'playlist'):
                try:
                    self.player.current_index = self.player.playlist.index(file_path)
                    print(f"🎵 Reproduciendo índice {self.player.current_index}: {os.path.basename(file_path)}")
                except ValueError:
                    print(f"⚠️ Archivo no está en playlist: {file_path}")
                    self.player.current_index = -1
            
            self.player.play_file(file_path)
            
            if self.winfo_exists():
                self.status_label.configure(
                    text=f"▶ Reproduciendo: {os.path.basename(file_path)}",
                    text_color="#2ECC71"
                )
        except Exception as e:
            print(f"❌ Error en _play_from_list: {e}")
            if self.winfo_exists():
                self.status_label.configure(text=f"Error: {e}", text_color="#E74C3C")

    def _handle_player_callback(self, event: str):
        """Callback del player con protección y actualización de UI"""
        
        def safe_update(func):
            if self.winfo_exists():
                try:
                    func()
                except tk.TclError:
                    pass
        
        if event == "playing":
            if 0 <= self.player.current_index < len(self.player.playlist):
                fname = os.path.basename(self.player.playlist[self.player.current_index])
                safe_update(lambda: self.status_label.configure(
                    text=f"▶ Reproduciendo: {fname}", text_color="#2ECC71"))
                    
        elif event == "finished":
            safe_update(lambda: self.status_label.configure(text="Siguiente pista...", text_color="#FFA500"))
            
        elif event in ("next_ready", "prev_ready"):
            if self.player.playlist and 0 <= self.player.current_index < len(self.player.playlist):
                target_file = self.player.playlist[self.player.current_index]
                self.after(0, lambda: self._play_from_list(target_file) if self.winfo_exists() else None)
            else:
                safe_update(lambda: self.status_label.configure(text="Fin de la lista", text_color="#888"))
                
        elif event.startswith("error"):
            safe_update(lambda: self.status_label.configure(text="Error al reproducir", text_color="#E74C3C"))

    def _stop_playback(self):
        """Detiene la reproducción actual"""
        self.player.stop()
        self.status_label.configure(text="⏹ Detenido")

    def _next_track(self):
        """Avanza a la siguiente pista"""
        self.player.next_track()

    def _prev_track(self):
        """Retrocede a la pista anterior"""
        self.player.prev_track()

    def _pause_playback(self):
        """Pausa o reanuda la reproducción"""
        self.player.pause()
        # Actualizar estado visual
        if self.player.is_paused:
            self.status_label.configure(text="⏸ Pausado", text_color="#FFA500")
        else:
            if 0 <= self.player.current_index < len(self.player.playlist):
                fname = os.path.basename(self.player.playlist[self.player.current_index])
                self.status_label.configure(text=f"▶ Reproduciendo: {fname}", text_color="#2ECC71")
            else:
                self.status_label.configure(text="Reproduciendo", text_color="#2ECC71")

    # ═══════════════════════════════════════════════════════════
    # 🚪 CLEANUP AL CERRAR
    # ═══════════════════════════════════════════════════════════
    
    def _on_close(self):
        """Limpieza antes de cerrar la aplicación"""
        try:
            if hasattr(self, 'player'):
                self.player.stop()
            self._save_config('last_folder', self.current_folder)
            self._save_config('volume', self.volume_var.get())
        except:
            pass
        finally:
            self.destroy()