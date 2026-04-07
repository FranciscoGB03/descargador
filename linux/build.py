#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el ejecutable del YouTube Downloader
Compatible con Windows y Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_pyinstaller():
    """Verificar si PyInstaller está instalado"""
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    print("Instalando PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def create_executable():
    """Crear el ejecutable usando PyInstaller"""
    
    # Configuración según el sistema operativo
    current_os = platform.system().lower()
    
    if current_os == "windows":
        icon_path = "icon.ico" if os.path.exists("icon.ico") else None
        executable_name = "YouTubeDownloader.exe"
    else:
        icon_path = "icon.png" if os.path.exists("icon.png") else None
        executable_name = "YouTubeDownloader"
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Crear un solo archivo ejecutable
        "--windowed",  # Sin terminal (para GUI)
        "--name", executable_name,
        "--add-data", "requirements.txt:.",  # Incluir requirements
    ]
    
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    cmd.append("main.py")
    
    print(f"Creando ejecutable para {current_os}...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"¡Ejecutable creado exitosamente! Archivo: dist/{executable_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al crear el ejecutable: {e}")
        return False


def create_desktop_shortcut():
    """Crear acceso directo en el escritorio (solo para Linux)"""
    if platform.system().lower() != "linux":
        return
        
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.join(os.path.expanduser("~"), "Escritorio")
    
    if os.path.exists(desktop_dir):
        shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Downloader
Comment=Descarga videos y audio de YouTube
Exec={os.path.abspath('dist/YouTubeDownloader')}
Icon=applications-multimedia
Terminal=false
Categories=AudioVideo;Video;
"""
        
        shortcut_path = os.path.join(desktop_dir, "YouTubeDownloader.desktop")
        with open(shortcut_path, "w") as f:
            f.write(shortcut_content)
        
        # Hacer el acceso directo ejecutable
        os.chmod(shortcut_path, 0o755)
        print(f"Acceso directo creado en: {shortcut_path}")


def main():
    print("=== YouTube Downloader - Generador de Ejecutable ===")
    print(f"Sistema operativo: {platform.system()}")
    print(f"Python: {sys.version}")
    print()
    
    # Verificar PyInstaller
    if not check_pyinstaller():
        print("PyInstaller no está instalado.")
        response = input("¿Desea instalar PyInstaller? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'sí', 'si']:
            install_pyinstaller()
        else:
            print("No se puede continuar sin PyInstaller.")
            return
    
    # Crear el ejecutable
    if create_executable():
        print("\n=== Proceso completado ===")
        print("El ejecutable se encuentra en la carpeta 'dist/'")
        
        # Crear acceso directo en Linux
        create_desktop_shortcut()
        
        print("\nPara distribuir la aplicación:")
        print("1. Copia el archivo ejecutable de la carpeta 'dist/'")
        print("2. Puedes compartirlo directamente con otros usuarios")
        print("3. No requiere instalación de Python para funcionar")
        
        if platform.system().lower() == "windows":
            print("\nPara Windows:")
            print("- El archivo .exe puede ser ejecutado directamente")
            print("- Puedes crear un acceso directo en el escritorio")
        else:
            print("\nPara Linux:")
            print("- El archivo ejecutable puede ser ejecutado directamente")
            print("- Se ha creado un acceso directo en tu escritorio")
    else:
        print("No se pudo crear el ejecutable. Revisa los mensajes de error.")


if __name__ == "__main__":
    main()
