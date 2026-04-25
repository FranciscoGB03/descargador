#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar FFmpeg estático para Linux
Incluye ffmpeg, ffplay y ffprobe con verificación
"""

import os
import sys
import urllib.request
import tarfile
import shutil
import subprocess
from pathlib import Path


def download_ffmpeg():
    """Descarga FFmpeg estático para Linux"""
    
    # URL de FFmpeg estático para Linux (amd64)
    ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    
    project_root = Path(__file__).parent.parent
    bin_dir = project_root / "bin" / "linux"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    temp_file = project_root / "ffmpeg.tar.xz"
    extract_dir = project_root / "ffmpeg_temp"
    
    downloaded_binaries = []
    
    try:
        print(f"📥 Descargando FFmpeg desde: {ffmpeg_url}")
        print("⏳ Esto puede tardar unos minutos (~70MB)...")
        
        # Descargar
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            sys.stdout.write(f"\r📥 Progreso: {percent:.1f}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(ffmpeg_url, temp_file, report_progress)
        print("\n✅ Descarga completada")
        
        # Extraer
        print("📦 Extrayendo...")
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()
        
        with tarfile.open(temp_file, "r:xz") as tar:
            tar.extractall(extract_dir)
        
        # Buscar los binarios
        extracted_folders = list(extract_dir.glob("ffmpeg-*-amd64-static"))
        if not extracted_folders:
            print("❌ No se encontró la carpeta de FFmpeg extraída")
            return False
        
        ffmpeg_folder = extracted_folders[0]
        print(f"📁 Carpeta extraída: {ffmpeg_folder.name}")
        
        # Listar qué binarios existen realmente
        available = []
        for binary in ["ffmpeg", "ffplay", "ffprobe"]:
            src = ffmpeg_folder / binary
            if src.exists():
                available.append(binary)
                print(f"  ✓ {binary} disponible en la descarga")
            else:
                print(f"  ✗ {binary} NO está en la descarga")
        
        # Copiar binarios disponibles
        print("\n📋 Copiando binarios a bin/linux...")
        for binary in available:
            src = ffmpeg_folder / binary
            dst = bin_dir / binary
            
            try:
                shutil.copy2(src, dst)
                os.chmod(dst, 0o755)  # Hacer ejecutable
                print(f"  ✅ {binary} copiado")
                downloaded_binaries.append(binary)
            except Exception as e:
                print(f"  ❌ Error copiando {binary}: {e}")
        
        # === Si falta ffplay, intentar descargarlo por separado ===
        if "ffplay" not in downloaded_binaries:
            print("\n⚠️  ffplay no estaba en el paquete principal")
            print("🔄 Intentando descargar ffplay por separado...")
            
            ffplay_url = "https://johnvansickle.com/ffmpeg/releases/ffplay-release-amd64-static.tar.xz"
            ffplay_temp = project_root / "ffplay.tar.xz"
            ffplay_extract = project_root / "ffplay_temp"
            
            try:
                # Descargar ffplay
                urllib.request.urlretrieve(ffplay_url, ffplay_temp)
                
                # Extraer
                if ffplay_extract.exists():
                    shutil.rmtree(ffplay_extract)
                ffplay_extract.mkdir()
                
                with tarfile.open(ffplay_temp, "r:xz") as tar:
                    tar.extractall(ffplay_extract)
                
                # Buscar y copiar ffplay
                ffplay_folders = list(ffplay_extract.glob("ffplay-*-amd64-static"))
                if ffplay_folders:
                    ffplay_src = ffplay_folders[0] / "ffplay"
                    ffplay_dst = bin_dir / "ffplay"
                    
                    if ffplay_src.exists():
                        shutil.copy2(ffplay_src, ffplay_dst)
                        os.chmod(ffplay_dst, 0o755)
                        print(f"  ✅ ffplay descargado y copiado por separado")
                        downloaded_binaries.append("ffplay")
                    else:
                        print(f"  ❌ ffplay no encontrado en descarga separada")
                
            except Exception as e:
                print(f"  ⚠️  No se pudo descargar ffplay por separado: {e}")
                print(f"  💡 Usando ffplay del sistema como fallback")
            
            finally:
                # Limpieza ffplay
                if ffplay_temp.exists():
                    ffplay_temp.unlink()
                if ffplay_extract.exists():
                    shutil.rmtree(ffplay_extract)
        
        # Resumen final
        print(f"\n✅ Binarios instalados en: {bin_dir.absolute()}")
        print(f"📦 Incluidos: {', '.join(downloaded_binaries)}")
        
        total_size = sum(f.stat().st_size for f in bin_dir.rglob('*') if f.is_file())
        print(f"📁 Tamaño total: {total_size / 1024 / 1024:.1f} MB")
        
        # Verificación final
        missing = set(["ffmpeg", "ffplay", "ffprobe"]) - set(downloaded_binaries)
        if missing:
            print(f"\n⚠️  Binarios faltantes: {', '.join(missing)}")
            print(f"💡 La app usará los del sistema para esos binarios")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpieza
        if temp_file.exists():
            temp_file.unlink()
        if extract_dir.exists():
            shutil.rmtree(extract_dir)


def verify_binaries():
    """Verifica que los binarios sean ejecutables válidos"""
    project_root = Path(__file__).parent.parent
    bin_dir = project_root / "bin" / "linux"
    
    print("\n🔍 Verificando binarios...")
    for binary in ["ffmpeg", "ffplay", "ffprobe"]:
        binary_path = bin_dir / binary
        if binary_path.exists():
            # Verificar que es ejecutable
            if os.access(binary_path, os.X_OK):
                # Verificar que es un ELF válido
                try:
                    result = subprocess.run(
                        ["file", str(binary_path)],
                        capture_output=True, text=True, timeout=5
                    )
                    if "ELF" in result.stdout:
                        print(f"  ✅ {binary}: OK")
                    else:
                        print(f"  ⚠️  {binary}: formato desconocido")
                except:
                    print(f"  ℹ️  {binary}: verificación omitida")
            else:
                print(f"  ❌ {binary}: sin permisos de ejecución")
                print(f"     Ejecuta: chmod +x {binary_path}")
        else:
            print(f"  ❌ {binary}: no encontrado")


if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Descargador de FFmpeg para Linux")
    print("=" * 60)
    
    if download_ffmpeg():
        verify_binaries()
        print("\n🎉 ¡Listo! Ahora puedes compilar con:")
        print("   python3 build_linux.py")
    else:
        print("\n❌ No se pudo descargar FFmpeg")
        sys.exit(1)