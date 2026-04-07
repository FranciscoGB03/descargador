#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Video/Audio Downloader
Compatible with Windows and Linux
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from pathlib import Path
import yt_dlp
from urllib.parse import urlparse


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp4")
        self.quality_var = tk.StringVar(value="high")
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        
        # Estilo personalizado para la barra de progreso
        style.configure('Custom.Horizontal.TProgressbar',
                      background='#4CAF50',  # Verde brillante
                      troughcolor='#E0E0E0',  # Gris claro para el fondo
                      bordercolor='#CCCCCC',
                      lightcolor='#4CAF50',
                      darkcolor='#45A049')
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="YouTube Downloader", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL del video
        url_label = ttk.Label(main_frame, text="URL del video:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        # Formato de salida
        format_label = ttk.Label(main_frame, text="Formato:")
        format_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Radiobutton(format_frame, text="MP4 (Video)", variable=self.format_var, 
                       value="mp4").grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="MP3 (Audio)", variable=self.format_var, 
                       value="mp3").grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="MKV (Video)", variable=self.format_var, 
                       value="mkv").grid(row=0, column=2)
        
        # Calidad (solo para video)
        quality_label = ttk.Label(main_frame, text="Calidad:")
        quality_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Radiobutton(quality_frame, text="Alta", variable=self.quality_var, 
                       value="high").grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(quality_frame, text="Media", variable=self.quality_var, 
                       value="medium").grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(quality_frame, text="Baja", variable=self.quality_var, 
                       value="low").grid(row=0, column=2)
        
        # Ruta de descarga
        path_label = ttk.Label(main_frame, text="Carpeta de descarga:")
        path_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.path_label = ttk.Label(path_frame, text=self.download_path, style='Info.TLabel')
        self.path_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(path_frame, text="Cambiar", command=self.change_download_path).grid(row=0, column=1, padx=(10, 0))
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           variable=self.progress_var, 
                                           maximum=100, 
                                           length=400,
                                           style='Custom.Horizontal.TProgressbar')
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(main_frame, text="Listo para descargar", style='Info.TLabel')
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        self.download_button = ttk.Button(button_frame, text="Descargar", command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Salir", command=self.root.quit).grid(row=0, column=1, padx=5)
        
    def change_download_path(self):
        new_path = filedialog.askdirectory(initialdir=self.download_path)
        if new_path:
            self.download_path = new_path
            self.path_label.config(text=self.download_path)
            
    def validate_url(self, url):
        try:
            parsed = urlparse(url)
            return parsed.netloc in ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']
        except:
            return False
            
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL de YouTube")
            return
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "URL no válida. Debe ser una URL de YouTube")
            return
            
        # Deshabilitar botón durante la descarga
        self.download_button.config(state='disabled')
        self.status_label.config(text="Iniciando descarga...")
        self.progress_var.set(0)
        
        # Iniciar descarga en hilo separado
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()
        
    def download_video(self, url):
        try:
            format_choice = self.format_var.get()
            quality = self.quality_var.get()
            
            # Limpiar URL para evitar playlists
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
                url = f'https://www.youtube.com/watch?v={video_id}'
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
                url = f'https://www.youtube.com/watch?v={video_id}'
            
            # Configuración de yt-dlp
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'js-runtimes': 'deno',
                'ignoreerrors': True,  # Ignorar errores y continuar
            }
            
            if format_choice == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'writethumbnail': False,
                })
            elif format_choice == 'mp4':
                if quality == 'high':
                    ydl_opts['format'] = 'best[height<=720]/best'
                elif quality == 'medium':
                    ydl_opts['format'] = 'best[height<=480]/best'
                else:  # low
                    ydl_opts['format'] = 'worst/worst[height<=360]'
                    
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                })
            elif format_choice == 'mkv':
                if quality == 'high':
                    ydl_opts['format'] = 'best[height<=720]/best'
                elif quality == 'medium':
                    ydl_opts['format'] = 'best[height<=480]/best'
                else:  # low
                    ydl_opts['format'] = 'worst/worst[height<=360]'
                    
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mkv',
                    }],
                })
            
            # Realizar descarga
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            self.root.after(0, self.download_complete)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.download_error(error_msg))
            
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0.0%')
            # Limpiar códigos de color ANSI
            import re
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
            try:
                percent = float(percent_str.strip('%').replace(',', '.'))
                self.root.after(0, lambda p=percent: self.progress_var.set(p))
            except ValueError:
                # Si hay error, usar el valor numérico directo
                percent = d.get('_percent_str', '0.0%')
                if isinstance(percent, (int, float)):
                    self.root.after(0, lambda p=percent: self.progress_var.set(p))
            
            speed_str = d.get('_speed_str', '0 B/s')
            eta_str = d.get('_eta_str', '00:00')
            
            status_text = f"Descargando... {percent_str} - Velocidad: {speed_str} - Tiempo restante: {eta_str}"
            self.root.after(0, lambda: self.status_label.config(text=status_text))
            
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_label.config(text="Procesando archivo..."))
            
    def download_complete(self):
        self.progress_var.set(100)
        self.status_label.config(text="¡Descarga completada!")
        self.download_button.config(state='normal')
        messagebox.showinfo("Éxito", "¡El video se ha descargado correctamente!")
        
    def download_error(self, error_msg):
        self.status_label.config(text="Error en la descarga")
        self.download_button.config(state='normal')
        messagebox.showerror("Error", f"No se pudo descargar el video:\n{error_msg}")


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
