#  Requisitos de FFmpeg/FFplay

## 📋 ¿Qué es FFplay y por qué lo necesito?

**FFplay** es un reproductor de multimedia simple pero potente que permite reproducir videos y audio. Es parte del paquete **FFmpeg**.

### ¿Para qué lo usa esta aplicación?

- ✅ **Descargar videos**: Usa `ffmpeg` (incluido en la app) 
- ✅ **Convertir formatos**: Usa `ffmpeg` (incluido en la app)
- ▶️ **Reproducir contenido**: Usa `ffplay` (requiere instalación)

---

## 🎯 Resumen rápido

| Función | Estado |
|---------|--------|
| **Descargar videos de YouTube** | ✅ Funciona sin instalar nada |
| **Convertir a MP3/MP4/MKV** | ✅ Funciona sin instalar nada |
| **Reproducir audio/video** | ⚠️ Requiere `ffplay` instalado |

> 💡 **Nota**: `ffmpeg` y `ffprobe` están incluidos en la aplicación (~150MB).  
> Solo necesitas instalar `ffplay` si quieres reproducir contenido desde la app.

---

##  Instalación de FFmpeg (incluye ffplay)

### 🔍 Verificar si ya lo tienes

Abre una terminal y ejecuta:

```bash
ffplay -version