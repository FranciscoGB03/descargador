# Guía de Instalación y Uso

## Pasos para configurar el proyecto

### 1. Crear entorno virtual
```bash
python3 -m venv venv
```

### 2. Activar entorno virtual
```bash
# En Linux/macOS
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### 3. Instalar dependencias de Python
```bash
pip install yt-dlp pyinstaller
```

### 4. Instalar dependencias del sistema (solo Linux)
```bash
sudo apt-get update
sudo apt-get install python3-tk ffmpeg
```

### 5. Instalar Deno (mejora extracción de YouTube)
```bash
curl -fsSL https://deno.land/install.sh | sh
export PATH="$HOME/.deno/bin:$PATH"
```

### 6. Ejecutar la aplicación
```bash
python main.py
```

### 7. Generar ejecutable (opcional)
```bash
python build.py
```

## Notas importantes

- El entorno virtual evita instalar paquetes globalmente
- FFmpeg es necesario para conversión de formatos
- Deno mejora la extracción de videos de YouTube
- El ejecutable generado funciona sin Python instalado
- En Linux el ejecutable será `YouTubeDownloader`

## Requisitos del sistema

### Linux
- Python 3.7+
- python3-tk
- ffmpeg
- deno (opcional pero recomendado)

### Windows
- Python 3.7+
- FFmpeg (agregar al PATH)
- Deno (opcional pero recomendado)
