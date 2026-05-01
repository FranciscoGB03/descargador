#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para verificar y actualizar yt-dlp en tiempo de ejecución.
Fix para PyInstaller: Manejo de SSL y Logs persistentes.
"""

import urllib.request
import urllib.error
import ssl
import json
import subprocess
import os
import stat
import platform
import logging
from pathlib import Path
from typing import Tuple

# Configuración de LOGS (para ver errores cuando no hay terminal)
LOG_DIR = Path.home() / ".config" / "youtube_downloader"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "updater.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def _get_ssl_context():
    """Crea un contexto SSL seguro que funcione incluso en binarios compilados"""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        # Si no tiene certifi, intenta cargar los del sistema, pero permite fallos controlados
        logging.warning("Certifi no encontrado, usando contexto por defecto.")
        return ssl.create_default_context()

def get_ytdlp_path() -> str:
    system = platform.system()
    if system == "Windows":
        local_path = Path.home() / "AppData" / "Local" / "youtube_downloader" / "yt-dlp.exe"
    else:
        local_path = Path.home() / ".local" / "bin" / "yt-dlp"
        
    if local_path.exists():
        return str(local_path)
    return "yt-dlp"

def check_versions() -> Tuple[str, str]:
    """Retorna (versión_actual, versión_más_reciente)"""
    try:
        logging.info("Iniciando verificación de versiones...")
        
        # 1. Versión local
        try:
            res = subprocess.run(
                [get_ytdlp_path(), "--version"], 
                capture_output=True, text=True, timeout=5
            )
            current = res.stdout.strip() if res.returncode == 0 else "unknown"
            logging.info(f"Versión actual detectada: {current}")
        except Exception as e:
            current = "unknown"
            logging.error(f"Error obteniendo versión actual: {e}")

        # 2. Versión GitHub (API oficial) - USANDO SSL FIX
        ctx = _get_ssl_context()
        req = urllib.request.Request("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest")
        req.add_header("User-Agent", "YouTubeDownloader-App/1.0")
        
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            latest = data.get("tag_name", "unknown").lstrip("v")
            logging.info(f"Última versión en GitHub: {latest}")
            
        return current, latest
        
    except Exception as e:
        logging.error(f"Error grave en check_versions: {e}")
        return "unknown", "unknown"


def download_update() -> Tuple[bool, str]:
    """Descarga la última versión oficial"""
    system = platform.system()
    try:
        logging.info("Iniciando descarga de actualización...")
        
        if system == "Windows":
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
            filename = "yt-dlp.exe"
            dest_dir = Path.home() / "AppData" / "Local" / "youtube_downloader"
        else:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            filename = "yt-dlp"
            dest_dir = Path.home() / ".local" / "bin"

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename
        
        ctx = _get_ssl_context()
        logging.info(f"Descargando desde: {url}")
        
        with urllib.request.urlopen(url, context=ctx, timeout=60) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
                
        if system != "Windows":
            os.chmod(dest_path, os.stat(dest_path).st_mode | stat.S_IEXEC)
            
        logging.info(f"Descarga exitosa: {dest_path}")
        return True, f"✅ Actualizado a: {dest_path}"
        
    except Exception as e:
        logging.error(f"Error descargando: {e}")
        return False, f"❌ Error descargando: {str(e)}"