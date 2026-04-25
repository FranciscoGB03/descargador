import os
import subprocess
from typing import List, Callable

class MediaLibrary:
    def __init__(
        self, base_dir: str, ffmpeg_path: str = "ffmpeg"
    ):
        # ffplay suele estar en la misma carpeta bin que ffmpeg
        bin_dir = os.path.dirname(ffmpeg_path)
        candidates = [
            os.path.join(bin_dir, "ffplay.exe"),
            os.path.join(base_dir, "ffplay.exe"),
        ]
        self.ffplay_path = next((p for p in candidates if os.path.exists(p)), "ffplay")

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

    def play_file(self, file_path: str, callback: Callable[[str, str], None]):
        """Reproduce un archivo usando ffplay en ventana independiente"""
        if not os.path.exists(file_path):
            callback("error", "Archivo no encontrado")
            return
        try:
            # -autoexit: cierra la ventana al terminar
            # -window_title: muestra nombre del archivo en la barra
            subprocess.Popen([
                self.ffplay_path, 
                "-autoexit", 
                "-window_title", os.path.basename(file_path),
                file_path
            ])
            callback("info", f"▶️ Reproduciendo: {os.path.basename(file_path)}")
        except Exception as e:
            callback("error", f"❌ Error al reproducir: {str(e)}")