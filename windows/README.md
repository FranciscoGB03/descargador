# Pasos para el compilado

# 0. Ambiente virtual
python -m venv venv

# 1. Activa tu ambiente virtual
.\venv\Scripts\Activate

# 2. Instala dependencias requirements.txt
pip install -r requirements.txt

# 3. Ejecuta pyinstaller con las opciones adecuadas
pyinstaller --onefile --windowed --name "YouTubeDownloader" --icon "icono.ico" --add-data "ffmpeg-8.1-essentials_build;ffmpeg-8.1-essentials_build" main.py