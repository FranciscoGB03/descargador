# Guía para generar ejecutable de Windows

## Requisitos para Windows

### 1. Instalar Python
- Descargar Python 3.7+ desde https://python.org
- Marcar "Add Python to PATH" durante la instalación

### 2. Instalar dependencias del sistema
- Descargar FFmpeg desde https://ffmpeg.org/download.html
- Extraer y agregar la carpeta `bin` al PATH de Windows
- Descargar Deno desde https://deno.land y agregar al PATH (opcional)

### 3. Crear entorno virtual
```cmd
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar dependencias de Python
```cmd
pip install yt-dlp pyinstaller
```

### 5. Generar ejecutable
```cmd
python build.py
```

## Archivos generados

### Para Linux
- **Archivo**: `dist/YouTubeDownloader` (20.5 MB)
- **Acceso directo**: Escritorio → YouTubeDownloader.desktop
- **Requisitos**: FFmpeg instalado en el sistema

### Para Windows
- **Archivo**: `dist/YouTubeDownloader.exe` (aproximadamente 25-30 MB)
- **Requisitos**: FFmpeg en el PATH del sistema

## Distribución

### Linux
```bash
# Copiar el ejecutable
cp dist/YouTubeDownloader /ruta/de/distribucion/

# Hacerlo ejecutable
chmod +x YouTubeDownloader

# Ejecutar
./YouTubeDownloader
```

### Windows
```cmd
# Copiar el ejecutable
copy dist\YouTubeDownloader.exe C:\ruta\de\distribucion\

# Ejecutar (doble clic)
YouTubeDownloader.exe
```

## Notas importantes

1. **Tamaño del ejecutable**: ~20-30 MB (normal para PyInstaller)
2. **Independiente**: No requiere instalación de Python
3. **FFmpeg requerido**: Debe estar instalado en el sistema destino
4. **Deno opcional**: Mejora extracción pero no es obligatorio

## Verificación

### Linux
```bash
# Verificar permisos
ls -la dist/YouTubeDownloader

# Probar ejecución
./dist/YouTubeDownloader
```

### Windows
```cmd
# Verificar archivo
dir dist\YouTubeDownloader.exe

# Probar ejecución
dist\YouTubeDownloader.exe
```

## Solución de problemas

### Error: "FFmpeg not found"
- Instalar FFmpeg y agregar al PATH
- Para Linux: `sudo apt-get install ffmpeg`
- Para Windows: Descargar desde ffmpeg.org

### Error: "Permission denied"
- Linux: `chmod +x YouTubeDownloader`
- Windows: Ejecutar como administrador

### Error: "Antivirus bloquea"
- Agregar excepción en el antivirus
- Es un falso positivo común con PyInstaller
