#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestión de biblioteca de medios local
Compatible con Windows y Linux
"""

import os
import subprocess
from typing import List, Callable, Optional
from core.utils import get_ffplay_path, get_base_dir


class MediaLibrary:
    def __init__(
        self, 
        base_dir: Optional[str] = None, 
        ffmpeg_path: str = None,
        callback: Callable[[str, str], None] = None
    ):
        self.base_dir = base_dir or get_base_dir()
        self.callback = callback or (lambda e, m: None)
        self.ffplay_path = get_ffplay_path(self.base_dir)

    def scan_folder(self, folder: str) -> List[str]:
        """Devuelve lista de archivos multimedia soportados"""
        if not os.path.isdir(folder):
            return []
        supported = ('.mp3', '.mp4', '.mkv', '.webm', '.m4a', '.wav', '.flac', '.opus')
        try:
            return sorted([
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(supported)
            ])
        except PermissionError:
            return []
        except Exception:
            return []

    def play_file(self, file_path: str, callback: Callable[[str, str], None] = None):
        """Reproduce un archivo usando ffplay en ventana independiente"""
        cb = callback or self.callback
        
        if not os.path.exists(file_path):
            cb("error", "Archivo no encontrado")
            return
        
        try:
            cmd = [
                self.ffplay_path, 
                "-autoexit", 
                "-window_title", os.path.basename(file_path),
                file_path
            ]
            # Para Linux: separar proceso del padre
            subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            cb("info", f"▶️ Reproduciendo: {os.path.basename(file_path)}")
        except Exception as e:
            cb("error", f"❌ Error al reproducir: {str(e)}")