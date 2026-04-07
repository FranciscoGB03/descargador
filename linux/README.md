# YouTube Downloader

Un descargador de video y audio de YouTube compatible con Windows y Linux, con interfaz gráfica fácil de usar.

## Características

- 🎥 Descarga videos en formato MP4 y MKV
- 🎵 Descarga audio en formato MP3
- 🖥️ Interfaz gráfica intuitiva con tkinter
- 🪟 Compatible con Windows y Linux
- 📦 Genera ejecutable independiente (no requiere Python)
- 📊 Barra de progreso en tiempo real
- 🎯 Selección de calidad (Alta, Media, Baja)
- 📁 Carpeta de descarga personalizable

## Requisitos

- Python 3.7 o superior
- Conexión a internet

## Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <repository-url>
cd descargador
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

#### Opción A: Modo desarrollo
```bash
python main.py
```

#### Opción B: Generar ejecutable
```bash
python build.py
```

El ejecutable se creará en la carpeta `dist/`:
- Windows: `YouTubeDownloader.exe`
- Linux: `YouTubeDownloader`

## Uso

1. **Iniciar la aplicación**: Ejecuta el archivo `main.py` o el ejecutable generado
2. **Pegar la URL**: Ingresa la URL del video de YouTube que quieres descargar
3. **Seleccionar formato**: Elige entre MP4 (video), MP3 (audio), o MKV (video)
4. **Elegir calidad**: Selecciona la calidad deseada (solo para video)
5. **Carpeta de descarga**: Usa la carpeta predeterminada (Downloads) o elige otra
6. **Descargar**: Haz clic en el botón "Descargar" y espera a que termine

## Formatos soportados

### Video
- **MP4**: Formato universal compatible con la mayoría de los dispositivos
- **MKV**: Alta calidad, soporta múltiples pistas de audio/subtítulos

### Audio
- **MP3**: Formato de audio comprimido, compatible con todos los dispositivos

## Calidades disponibles

- **Alta**: Hasta 720p (video) / 192 kbps (audio)
- **Media**: Hasta 480p (video) / 128 kbps (audio)
- **Baja**: Hasta 360p (video) / 96 kbps (audio)

## Estructura del proyecto

```
descargador/
├── main.py              # Aplicación principal
├── build.py             # Script para generar ejecutable
├── requirements.txt     # Dependencias de Python
├── README.md           # Este archivo
└── dist/               # Carpeta con el ejecutable (generada)
```

## Dependencias

- `yt-dlp`: Biblioteca principal para descargar videos de YouTube
- `tkinter`: Interfaz gráfica (incluida con Python)

## Solución de problemas

### Error: "URL no válida"
- Asegúrate de que la URL sea de YouTube (youtube.com, youtu.be)
- Verifica que el video sea público y no privado

### Error: "No se pudo descargar el video"
- Verifica tu conexión a internet
- Algunos videos pueden tener restricciones de descarga
- Intenta con otra calidad o formato

### En Linux: "Permiso denegado"
- Asegúrate de que el ejecutable tenga permisos de ejecución:
```bash
chmod +x dist/YouTubeDownloader
```

### En Windows: "Antivirus bloquea el archivo"
- El ejecutable puede ser detectado como falso positivo
- Agrega una excepción en tu antivirus para el archivo

## Desarrollo

### Modificar la aplicación
- El código principal está en `main.py`
- La interfaz usa tkinter y es completamente personalizable
- La lógica de descarga usa yt-dlp

### Regenerar el ejecutable
- Después de modificar el código, ejecuta `python build.py`
- El nuevo ejecutable reemplazará al anterior en `dist/`

## Licencia

Este proyecto es de código abierto y libre para usar, modificar y distribuir.

## Créditos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp): Biblioteca principal para descargas
- [tkinter](https://docs.python.org/3/library/tkinter.html): Interfaz gráfica
- [PyInstaller](https://pyinstaller.org/): Creación de ejecutables
