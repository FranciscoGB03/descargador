import customtkinter as ctk
import tkinter.filedialog as filedialog
import os
from core.downloader import YouTubeDownloader

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader Pro")
        self.geometry("620x580")
        self.resizable(False, False)

        # Tema moderno
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.downloader = YouTubeDownloader(self._handle_callback)
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Título
        ctk.CTkLabel(main_frame, text="🎥 YouTube Downloader", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # URL
        ctk.CTkLabel(main_frame, text="URL del Video / Playlist:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.url_entry = ctk.CTkEntry(main_frame, placeholder_text="https://www.youtube.com/...", height=35)
        self.url_entry.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        # Carpeta
        ctk.CTkLabel(main_frame, text="Carpeta de destino:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, sticky="w", pady=(0, 5))
        folder_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        folder_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        self.folder_entry = ctk.CTkEntry(folder_frame, placeholder_text="Selecciona carpeta...", state="readonly", height=35)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(folder_frame, text="📁", width=45, height=35, command=self._browse_folder).pack(side="right", padx=(10, 0))

        # Opciones
        opts_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#1A1A1A")
        opts_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(opts_frame, text="Formato:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(15, 10), pady=10, sticky="w")
        self.fmt_var = ctk.StringVar(value="mp4")
        for i, txt in enumerate(["MP4", "MP3", "MKV"]):
            ctk.CTkRadioButton(opts_frame, text=txt, variable=self.fmt_var, value=txt.lower(), width=80).grid(row=0, column=i+1, padx=10, pady=10)

        ctk.CTkLabel(opts_frame, text="Modo:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts_frame, text="Descargar playlist completa", variable=self.playlist_var, command=self._toggle_items).grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkLabel(opts_frame, text="Rangos (ej: 1,3-5):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=(15, 10), pady=(0, 10), sticky="w")
        self.items_entry = ctk.CTkEntry(opts_frame, placeholder_text="Opcional", state="disabled", height=30, width=200)
        self.items_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # Botón
        self.download_btn = ctk.CTkButton(main_frame, text="⬇️ Descargar", height=45, font=ctk.CTkFont(size=18, weight="bold"), command=self._start_download)
        self.download_btn.grid(row=6, column=0, columnspan=2, pady=(10, 20), sticky="ew")

        # Progreso
        self.progress_bar = ctk.CTkProgressBar(main_frame, height=12, corner_radius=6)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(main_frame, text="Listo para descargar", text_color="#8A8A8A", font=ctk.CTkFont(size=13))
        self.status_label.grid(row=8, column=0, columnspan=2)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if folder:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="readonly")

    def _toggle_items(self):
        self.items_entry.configure(state="normal" if self.playlist_var.get() else "disabled")

    def _start_download(self):
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip() or "./descargas"
        if not url:
            self._handle_callback("error", "Por favor ingresa una URL válida.")
            return

        self.download_btn.configure(state="disabled", text="⏳ Procesando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Conectando con YouTube...", text_color="#4A90E2")

        self.downloader.start_download(
            url=url,
            fmt=self.fmt_var.get(),
            output_dir=folder,
            is_playlist=self.playlist_var.get(),
            items=self.items_entry.get().strip() if self.playlist_var.get() else None
        )

    def _handle_callback(self, event: str, data):
        # Thread-safe: actualiza la UI desde el hilo principal
        if event == "start":
            self.after(0, lambda: self.status_label.configure(text=data, text_color="#4A90E2"))
        elif event == "progress":
            pct, speed = data
            self.after(0, lambda: self.progress_bar.set(pct))
            self.after(0, lambda: self.status_label.configure(text=f"⚡ {speed} | {int(pct*100)}%", text_color="#B0B0B0"))
        elif event == "finished":
            self.after(0, lambda: self.status_label.configure(text=data, text_color="#2ECC71"))
            self.after(0, lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))
            self.after(0, lambda: self.progress_bar.set(1.0))
        elif event == "error":
            self.after(0, lambda: self.status_label.configure(text=data, text_color="#E74C3C"))
            self.after(0, lambda: self.download_btn.configure(state="normal", text="⬇️ Descargar"))
            self.after(0, lambda: self.progress_bar.set(0))