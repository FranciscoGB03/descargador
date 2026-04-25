import subprocess
import os
import threading
import time
from typing import List, Callable

class PlayerEngine:
    def __init__(self, ffmpeg_base_path: str, callback: Callable[[str], None]):
        self.ffmpeg_base_path = ffmpeg_base_path
        self.callback = callback
        self.playlist: List[str] = []
        self.current_index = -1
        self.is_playing = False
        self._process = None
        self._stop_event = threading.Event()
        self._is_loading = False

    def play_file(self, file_path: str):
        if self._is_loading:
            return
        self._is_loading = True
        print(f"🎵 Reproduciendo: {os.path.basename(file_path)}")

        self._cleanup_process()
        
        ffplay_path = os.path.join(os.path.dirname(self.ffmpeg_base_path), "ffplay.exe")
        if not os.path.exists(ffplay_path):
            ffplay_path = "ffplay"

        # ffplay en su propia ventana (más estable en Windows)
        cmd = [
            ffplay_path,
            "-i", file_path,
            "-autoexit",
            "-window_title", os.path.basename(file_path)
        ]

        try:
            self._start_time = time.time()
            self._process = subprocess.Popen(cmd)
            
            self.is_playing = True
            self.callback("playing")
            
            self._stop_event.clear()
            t = threading.Thread(target=self._monitor_process, daemon=True)
            t.start()
            
        except Exception as e:
            self._is_loading = False
            print(f"❌ Error: {e}")
            self.callback(f"error: {e}")

    def _monitor_process(self):
        if self._process:
            try:
                self._process.wait()
                duration = time.time() - self._start_time
                
                if duration < 1.0:
                    self.callback("error_ffplay")
                    return

            except Exception as e:
                print(f"Error monitor: {e}")
            
            if not self._stop_event.is_set() and self.is_playing:
                self.callback("finished")
                self.next_track()
        
        self._is_loading = False

    def _cleanup_process(self):
        self._stop_event.set()
        self.is_playing = False
        
        if self._process:
            try:
                if self._process.poll() is None:
                    self._process.terminate()
                    try:
                        self._process.wait(timeout=2)
                    except:
                        self._process.kill()
            except:
                pass
            self._process = None

    def stop(self):
        self._cleanup_process()
        self._is_loading = False

    def next_track(self):
        if self._is_loading or not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.callback("next_ready")

    def prev_track(self):
        if self._is_loading or not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.callback("prev_ready")