import customtkinter as ctk
import tkinter as tk
import tkinter.filedialog as filedialog
import os
import sys
from core.downloader import YouTubeDownloader
from core.player import PlayerEngine

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader & Player")
        self.geometry("700x600")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.ffmpeg_path = self._find_ffmpeg()
        self.current_folder = ""

        try:
            self.downloader = YouTubeDownloader(self._handle_download_callback)
            self.player = PlayerEngine(self.ffmpeg_path, self._handle_player_callback)
        except Exception as e:
            print(f"Error cargando módulos: {e}")
            return

        self._setup_ui()

    def _safe_ui_update(self, callback):
        if not self.winfo_exists():
            return
        try:
            self.after(0, callback)
        except tk.TclError:
            pass

    def _find_ffmpeg(self):
        candidates = [
            os.path.join(self.base_dir, "ffmpeg.exe"),
            os.path.join(self.base_dir, "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(self.base_dir, "ffmpeg-8.1-essentials_build", "bin", "ffmpeg.exe"),
        ]
        return next((p for p in candidates if os.path.exists(p)), "ffmpeg")

    def _setup_ui(self):
        self.tabview = ctk.CTkTabview(self, width=680, height=580, corner_radius=15)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        self.tabview.add("⬇️ Descargar")
        self.tabview.add("🎧 Biblioteca")

        self._setup_download_tab()
        self._setup_library_tab()

    def _setup_download_tab(self):
        tab = self.tabview.tab("⬇️ Descargar")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="URL del Video / Playlist:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", pady=(15, 5), padx=20)
        self.url_entry = ctk.CTkEntry(tab, placeholder_text="https://www.youtube.com/...", height=35)
        self.url_entry.grid(row=1, column=0, pady=(0, 15), sticky="ew", padx=20)

        ctk.CTkLabel(tab, text="Carpeta de destino:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, sticky="w", pady=(0, 5), padx=20)
        folder_frame = ctk.CTkFrame(tab, fg_color="transparent")
        folder_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15), padx=20)
        
        self.folder_entry = ctk.CTkEntry(folder_frame, placeholder_text="Selecciona carpeta...", state="readonly", height=35)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(folder_frame, text="📁", width=45, height=35, command=self._browse_folder).pack(side="right", padx=(10, 0))

        opts_frame = ctk.CTkFrame(tab, corner_radius=10, fg_color="#1A1A1A")
        opts_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15), padx=20)

        ctk.CTkLabel(opts_frame, text="Formato:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(15, 10), pady=10, sticky="w")
        self.fmt_var = ctk.StringVar(value="mp4")
        for i, txt in enumerate(["MP4", "MP3", "MKV"]):
            ctk.CTkRadioButton(opts_frame, text=txt, variable=self.fmt_var, value=txt.lower(), width=80).grid(row=0, column=i+1, padx=10, pady=10)

        ctk.CTkLabel(opts_frame, text="Modo:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts_frame, text="Descargar playlist completa", variable=self.playlist_var, command=self._toggle_items).grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkLabel(opts_frame, text="Rangos (ej: 1,3-5):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
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

        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(15, 10), padx=15)
        
        self.lib_folder_entry = ctk.CTkEntry(top_frame, placeholder_text="Selecciona carpeta...", state="readonly", height=35)
        self.lib_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(top_frame, text="📂", width=45, command=self._browse_lib_folder).pack(side="right")

        list_frame = ctk.CTkFrame(tab, fg_color="#1A1A1A", corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(list_frame, text="📂 Archivos", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, pady=10)
        
        self.playlist_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent", scrollbar_button_color="#555")
        self.playlist_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        btn_frame = ctk.CTkFrame(tab, fg_color="#1A1A1A", height=70, corner_radius=12)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        btn_frame.pack_propagate(False)

        ctk.CTkButton(btn_frame, text="⏮ Anterior", width=120, command=self._prev_track).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(btn_frame, text="⏹ Detener", width=120, fg_color="#E74C3C", hover_color="#C0392B", command=self._stop_playback).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(btn_frame, text="⏭ Siguiente", width=120, command=self._next_track).pack(side="left", padx=20, pady=20)

        self.status_label = ctk.CTkLabel(btn_frame, text="Selecciona una carpeta", text_color="#888", font=ctk.CTkFont(size=14))
        self.status_label.pack(side="right", padx=20)

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if folder:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="readonly")
            self.lib_folder_entry.configure(state="normal")
            self.lib_folder_entry.delete(0, "end")
            self.lib_folder_entry.insert(0, folder)
            self.lib_folder_entry.configure(state="readonly")
            self.current_folder = folder

    def _toggle_items(self):
        self.items_entry.configure(state="normal" if self.playlist_var.get() else "disabled")

    def _start_download(self):
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip() or "./descargas"
        if not url:
            self._safe_ui_update(lambda: self.dl_status.configure(text="Ingresa una URL válida", text_color="#E74C3C"))
            return

        self.download_btn.configure(state="disabled", text="⏳ Procesando...")
        self.progress_bar.set(0)
        self._safe_ui_update(lambda: self.dl_status.configure(text="Conectando...", text_color="#4A90E2"))

        self.downloader.start_download(
            url=url, fmt=self.fmt_var.get(), output_dir=folder,
            is_playlist=self.playlist_var.get(),
            items=self.items_entry.get().strip() if self.playlist_var.get() else None
        )

    def _handle_download_callback(self, event: str, data):
        if event == "start":
            self._safe_ui_update(lambda: self.dl_status.configure(text=data, text_color="#4A90E2"))
        elif event == "progress":
            pct, speed = data
            self._safe_ui_update(lambda: self.progress_bar.set(pct))
            self._safe_ui_update(lambda: self.dl_status.configure(text=f"⚡ {speed} | {int(pct*100)}%", text_color="#B0B0B0"))
        elif event == "finished":
            self._safe_ui_update(lambda: self.dl_status.configure(text="¡Listo!", text_color="#2ECC71"))
            self._safe_ui_update(lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))
            self._safe_ui_update(lambda: self.progress_bar.set(1.0))
            current_dl_folder = self.folder_entry.get().strip()
            if self.current_folder and current_dl_folder in self.current_folder:
                self._refresh_library()
        elif event == "error":
            self._safe_ui_update(lambda: self.dl_status.configure(text=data, text_color="#E74C3C"))
            self._safe_ui_update(lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))

    def _browse_lib_folder(self):
        folder = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if folder:
            self.current_folder = folder
            self.lib_folder_entry.configure(state="normal")
            self.lib_folder_entry.delete(0, "end")
            self.lib_folder_entry.insert(0, folder)
            self.lib_folder_entry.configure(state="readonly")
            self._refresh_library()

    def _refresh_library(self):
        if not self.current_folder:
            self.status_label.configure(text="Selecciona una carpeta primero")
            return

        if self.playlist_scroll.winfo_exists():
            for w in self.playlist_scroll.winfo_children():
                w.destroy()

        supported = ('.mp3', '.mp4', '.mkv', '.webm', '.m4a', '.flac')
        try:
            files = sorted([
                os.path.join(self.current_folder, f) for f in os.listdir(self.current_folder)
                if f.lower().endswith(supported)
            ])
        except Exception:
            files = []

        if not files:
            ctk.CTkLabel(self.playlist_scroll, text="No hay archivos multimedia", text_color="#666").pack(pady=20)
            return

        self.player.playlist = files
        self.player.current_index = -1

        for fpath in files:
            fname = os.path.basename(fpath)
            btn = ctk.CTkButton(
                self.playlist_scroll, 
                text=f"🎵 {fname}", 
                anchor="w", 
                height=40,
                command=lambda path=fpath: self._play_from_list(path)
            )
            btn.pack(fill="x", pady=2, padx=5)
        
        self.status_label.configure(text=f"{len(files)} archivos listos")

    def _play_from_list(self, file_path):
        try:
            self.player.play_file(file_path)
            self.status_label.configure(text=f"▶ Reproduciendo: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error UI: {e}")

    def _stop_playback(self):
        self.player.stop()
        self.status_label.configure(text="Detenido")

    def _next_track(self):
        self.player.next_track()

    def _prev_track(self):
        self.player.prev_track()

    def _handle_player_callback(self, event: str):
        if event == "playing":
            self._safe_ui_update(lambda: self.status_label.configure(text=f"▶ Reproduciendo: {os.path.basename(self.player.playlist[self.player.current_index]) if 0 <= self.player.current_index < len(self.player.playlist) else ''}", text_color="#2ECC71"))
        elif event == "finished":
            self._safe_ui_update(lambda: self.status_label.configure(text="Siguiente pista...", text_color="#FFA500"))
        elif event in ("next_ready", "prev_ready"):
            if self.player.playlist and 0 <= self.player.current_index < len(self.player.playlist):
                target_file = self.player.playlist[self.player.current_index]
                self._safe_ui_update(lambda: self._play_from_list(target_file))
            else:
                self._safe_ui_update(lambda: self.status_label.configure(text="Fin de la lista", text_color="#888"))
        elif event.startswith("error"):
            self._safe_ui_update(lambda: self.status_label.configure(text="Error al reproducir", text_color="#E74C3C"))