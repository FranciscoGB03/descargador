import yt_dlp
import os
import threading
from typing import Callable, Optional, Dict, Any

class YouTubeDownloader:
    def __init__(self, callback: Callable[[str, Any], None]):
        self.callback = callback
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _get_ffmpeg_path(self) -> str:
        import sys
        
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        candidates = [
            os.path.join(base_dir, "ffmpeg.exe"),
            os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(base_dir, "ffmpeg-8.1-essentials_build", "bin", "ffmpeg.exe"),
            os.path.join(base_dir, "bin", "ffmpeg.exe"),
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        import shutil
        return shutil.which("ffmpeg") or "ffmpeg"

    def start_download(self, url: str, fmt: str, output_dir: str, is_playlist: bool, items: Optional[str] = None):
        if self._thread and self._thread.is_alive():
            self.callback("error", "Ya hay una descarga en progreso.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, args=(url, fmt, output_dir, is_playlist, items), daemon=True)
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