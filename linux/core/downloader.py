#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de descarga de YouTube usando yt-dlp
Compatible con Windows y Linux
"""

import yt_dlp
import os
import threading
from typing import Callable, Optional, Dict, Any
from core.utils import get_ffmpeg_path, get_base_dir


class YouTubeDownloader:
    def __init__(self, callback: Callable[[str, Any], None], base_dir: Optional[str] = None):
        self.callback = callback
        self.base_dir = base_dir or get_base_dir()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _get_ffmpeg_path(self) -> str:
        return get_ffmpeg_path(self.base_dir)

    def start_download(self, url: str, fmt: str, output_dir: str, is_playlist: bool, items: Optional[str] = None):
        if self._thread and self._thread.is_alive():
            self.callback("error", "Ya hay una descarga en progreso.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, 
            args=(url, fmt, output_dir, is_playlist, items), 
            daemon=True
        )
        self._thread.start()

    def _progress_hook(self, d: Dict[str, Any]):
        if d['status'] == 'downloading':
            pct_str = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                pct_val = float(pct_str) / 100.0
            except ValueError:
                pct_val = 0.0
            speed = d.get('_speed_str', 'N/A')
            self.callback("progress", (pct_val, speed))
        elif d['status'] == 'finished':
            self.callback("progress", (1.0, "Procesando archivo..."))
        elif d['status'] == 'error':
            self.callback("error", "Error durante la descarga.")

    def _run(self, url: str, fmt: str, output_dir: str, is_playlist: bool, items: Optional[str]):
        try:
            ffmpeg_exe = self._get_ffmpeg_path()
            os.makedirs(output_dir, exist_ok=True)

            base_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': False,
                'no_warnings': False,
                'ffmpeg_location': ffmpeg_exe,
                'noplaylist': not is_playlist,
                'playlist_items': items if is_playlist and items else None,
                # Compatibilidad Linux
                'nocheckcertificate': True,
            }

            if fmt == "mp3":
                opts = {
                    **base_opts,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                opts = {
                    **base_opts,
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': fmt,
                }

            self.callback("start", "Iniciando descarga...")
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            self.callback("finished", "¡Descarga completada exitosamente!")
        except Exception as e:
            self.callback("error", f"Error: {str(e)}")