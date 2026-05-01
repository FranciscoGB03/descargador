#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades cross-platform para detección de FFmpeg/FFplay
Compatible con Windows y Linux
"""

import os
import shutil
import sys
import platform
from pathlib import Path
from typing import Optional
from core.ytdlp_updater import get_ytdlp_path as _updater_path


def get_base_dir() -> str:
    """Obtiene el directorio base de la aplicación (funciona en frozen y desarrollo)"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_ffmpeg_path(base_dir: Optional[str] = None) -> str:
    """
    Obtiene la ruta de ffmpeg.
    Prioridad: 1) Bundled en ejecutable, 2) bin/linux, 3) PATH del sistema
    """
    if base_dir is None:
        base_dir = get_base_dir()
    
    system = platform.system().lower()
    ffmpeg_name = "ffmpeg.exe" if system == "windows" else "ffmpeg"
    
    # === 1. Buscar en ejecutable PyInstaller ===
    if getattr(sys, 'frozen', False):
        candidates = []
        if system == "windows":
            candidates = [
                os.path.join(base_dir, "ffmpeg.exe"),
                os.path.join(base_dir, "bin", "ffmpeg.exe"),
            ]
        else:  # Linux
            candidates = [
                os.path.join(base_dir, "bin", "linux", "ffmpeg"),
                os.path.join(base_dir, "ffmpeg"),
            ]
        
        for path in candidates:
            if os.path.exists(path) and os.access(path, os.X_OK):
                print(f"✅ FFmpeg encontrado (bundled): {path}")
                return path
    
    # === 2. Buscar en bin/linux (modo desarrollo) ===
    if system == "linux":
        # Ruta relativa al directorio base
        bin_linux_path = os.path.join(base_dir, "bin", "linux", "ffmpeg")
        print(f"🔍 Buscando en: {bin_linux_path}")
        
        if os.path.exists(bin_linux_path):
            print(f"  ✓ Archivo existe")
            if os.access(bin_linux_path, os.X_OK):
                print(f"✅ FFmpeg encontrado (bin/linux): {bin_linux_path}")
                return bin_linux_path
            else:
                print(f"  ✗ No tiene permisos de ejecución")
        else:
            print(f"  ✗ Archivo no existe")
    
    # === 3. Buscar en PATH del sistema ===
    system_path = shutil.which(ffmpeg_name)
    if system_path:
        print(f"ℹ️  Usando FFmpeg del sistema: {system_path}")
        return system_path
    
    # === 4. Último recurso ===
    print(f"⚠️  FFmpeg no encontrado, usando: {ffmpeg_name}")
    return ffmpeg_name


def get_ffplay_path(base_dir: Optional[str] = None) -> str:
    """
    Obtiene la ruta de ffplay.
    Prioridad: 1) Bundled, 2) bin/linux, 3) PATH del sistema
    """
    if base_dir is None:
        base_dir = get_base_dir()
    
    system = platform.system().lower()
    ffplay_name = "ffplay.exe" if system == "windows" else "ffplay"
    
    # === 1. Buscar en ejecutable PyInstaller ===
    if getattr(sys, 'frozen', False):
        candidates = []
        if system == "windows":
            candidates = [
                os.path.join(base_dir, "ffplay.exe"),
                os.path.join(base_dir, "bin", "ffplay.exe"),
            ]
        else:  # Linux
            candidates = [
                os.path.join(base_dir, "bin", "linux", "ffplay"),
                os.path.join(base_dir, "ffplay"),
            ]
        
        for path in candidates:
            if os.path.exists(path) and os.access(path, os.X_OK):
                print(f"✅ FFplay encontrado (bundled): {path}")
                return path
    
    # === 2. Buscar en bin/linux (modo desarrollo) ===
    if system == "linux":
        bin_linux_path = os.path.join(base_dir, "bin", "linux", "ffplay")
        print(f"🔍 Buscando en: {bin_linux_path}")
        
        if os.path.exists(bin_linux_path):
            print(f"  ✓ Archivo existe")
            if os.access(bin_linux_path, os.X_OK):
                print(f"✅ FFplay encontrado (bin/linux): {bin_linux_path}")
                return bin_linux_path
            else:
                print(f"  ✗ No tiene permisos de ejecución")
                print(f"  💡 Ejecuta: chmod +x {bin_linux_path}")
        else:
            print(f"  ✗ Archivo no existe")
            # Listar qué hay en bin/linux si existe el directorio
            bin_dir = os.path.join(base_dir, "bin", "linux")
            if os.path.exists(bin_dir):
                try:
                    files = os.listdir(bin_dir)
                    print(f"  📁 Contenido de bin/linux: {files}")
                except:
                    pass
    
    # === 3. Buscar en PATH del sistema ===
    system_path = shutil.which(ffplay_name)
    if system_path:
        print(f"ℹ️  Usando FFplay del sistema: {system_path}")
        return system_path
    
    print(f"⚠️  FFplay no encontrado, usando: {ffplay_name}")
    return ffplay_name


def is_linux() -> bool:
    """Retorna True si el sistema es Linux"""
    return platform.system().lower() == "linux"


def is_windows() -> bool:
    """Retorna True si el sistema es Windows"""
    return platform.system().lower() == "windows"


def normalize_path(path: str) -> str:
    """Normaliza rutas para el sistema operativo actual"""
    return os.path.normpath(path)

def get_ytdlp_path() -> str:
    """Wrapper para usar la lógica centralizada de yt-dlp"""
    return _updater_path()