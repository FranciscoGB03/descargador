#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el ejecutable del YouTube Downloader en Linux
Con FFmpeg incluido
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


def check_ffmpeg_binaries():
    """Verifica que FFmpeg esté en bin/linux"""
    project_root = Path(__file__).parent
    bin_dir = project_root / "bin" / "linux"
    
    required = ["ffmpeg", "ffplay", "ffprobe"]
    missing = []
    
    for binary in required:
        binary_path = bin_dir / binary
        if not binary_path.exists():
            missing.append(binary)
    
    if missing:
        print(f"⚠️  FFmpeg no encontrado en: {bin_dir}")
        print(f"   Faltan: {', '.join(missing)}")
        print("\n📥 Descargando FFmpeg automáticamente...")
        
        # Ejecutar script de descarga
        download_script = project_root / "scripts" / "download_ffmpeg.py"
        if download_script.exists():
            result = subprocess.run([sys.executable, str(download_script)])
            if result.returncode != 0:
                print("❌ No se pudo descargar FFmpeg")
                return False
        else:
            print("❌ No se encontró scripts/download_ffmpeg.py")
            return False
    
    return True


def create_executable():
    """Crear ejecutable con FFmpeg incluido"""
    
    project_root = Path(__file__).parent
    bin_dir = project_root / "bin" / "linux"
    
    print("🔨 Compilando ejecutable para Linux con FFmpeg incluido...")
    print(f"📁 Binarios: {bin_dir.absolute()}")
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "YouTubeDownloader",
        "--add-data", "requirements.txt:.",
    ]
    
    # Icono si existe
    if (project_root / "icon.png").exists():
        cmd.extend(["--icon", str(project_root / "icon.png")])
    
    # Incluir FFmpeg
    if bin_dir.exists():
        print("📦 Incluyendo FFmpeg en el ejecutable...")
        cmd.extend([
            "--add-data", f"{bin_dir}:bin/linux",
        ])
        
        # Verificar tamaños
        for binary in ["ffmpeg", "ffplay", "ffprobe"]:
            binary_path = bin_dir / binary
            if binary_path.exists():
                size_mb = binary_path.stat().st_size / 1024 / 1024
                print(f"  📄 {binary}: {size_mb:.1f} MB")
    else:
        print("⚠️  Directorio bin/linux no encontrado")
        print("   Ejecuta: python3 scripts/download_ffmpeg.py")
        return False
    
    cmd.append("main.py")
    
    print(f"\n🚀 Comando: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, check=True, cwd=project_root)
        
        exe_path = project_root / "dist" / "YouTubeDownloader"
        if exe_path.exists():
            os.chmod(exe_path, 0o755)
            
            # Calcular tamaño total
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"\n✅ Ejecutable creado: {exe_path.absolute()}")
            print(f"📦 Tamaño: {size_mb:.1f} MB")
            print(f"\n🎉 ¡Listo para distribuir!")
            print(f"   Los usuarios NO necesitan instalar FFmpeg")
            print(f"   Solo ejecutan: ./YouTubeDownloader")
            
            return True
        else:
            print("❌ No se encontró el ejecutable en dist/")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al compilar: {e}")
        return False


def create_desktop_file():
    """Crear archivo .desktop para Linux"""
    project_root = Path(__file__).parent
    desktop_dir = Path.home() / "Desktop"
    if not desktop_dir.exists():
        desktop_dir = Path.home() / "Escritorio"
    
    if not desktop_dir.exists():
        return
    
    exe_path = project_root / "dist" / "YouTubeDownloader"
    icon_path = project_root / "icon.png"
    
    if not exe_path.exists():
        return
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Downloader
Comment=Descarga videos y audio de YouTube
Exec={exe_path.absolute()}
Icon={icon_path if icon_path.exists() else 'applications-multimedia'}
Terminal=false
Categories=AudioVideo;Network;Utility;
Keywords=youtube;download;video;audio;
StartupNotify=true
"""
    
    desktop_file = desktop_dir / "YouTubeDownloader.desktop"
    
    try:
        with open(desktop_file, "w") as f:
            f.write(desktop_content)
        os.chmod(desktop_file, 0o755)
        print(f"🚀 Acceso directo creado: {desktop_file}")
    except Exception as e:
        print(f"⚠️  No se pudo crear acceso directo: {e}")


def main():
    print("=" * 60)
    print("🐧 YouTube Downloader - Generador para Linux")
    print("=" * 60)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    
    if platform.system().lower() != "linux":
        print("⚠️  Este script es para Linux")
        resp = input("¿Continuar? (y/n): ").lower()
        if resp != 'y':
            return
    
    # Verificar FFmpeg
    if not check_ffmpeg_binaries():
        print("\n❌ Se requiere FFmpeg para continuar")
        return
    
    # Compilar
    if create_executable():
        create_desktop_file()
        
        print("\n" + "=" * 60)
        print("✅ ¡Proceso completado!")
        print("=" * 60)
        print("\n📁 El ejecutable está en: dist/YouTubeDownloader")
        print("\n🎯 Características:")
        print("   ✅ FFmpeg incluido (no requiere instalación)")
        print("   ✅ Un solo archivo ejecutable")
        print("   ✅ Portable - copiar y usar")
        print("\n📤 Para distribuir:")
        print("   1. Copia dist/YouTubeDownloader")
        print("   2. Compártelo con quien quieras")
        print("   3. ¡Listo! Sin dependencias")
    else:
        print("\n❌ No se pudo crear el ejecutable")


if __name__ == "__main__":
    main()