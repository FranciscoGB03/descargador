#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Downloader & Player - Punto de entrada principal
Startup limpio y cleanup seguro para Linux
"""

import sys
import os
import atexit

# Asegurar que el directorio del proyecto está en PYTHONPATH
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if application_path not in sys.path:
    sys.path.insert(0, application_path)

from ui.main_window import MainWindow


def main():
    try:
        app = MainWindow()
        
        # Función de limpieza centralizada
        def cleanup_and_close():
            try:
                if hasattr(app, 'player'):
                    app.player.stop()
            except:
                pass
            try:
                app.destroy()
            except:
                pass

        # 1. Cleanup al cerrar con la X de la ventana
        app.protocol("WM_DELETE_WINDOW", cleanup_and_close)
        
        # 2. Cleanup si el proceso termina por cualquier otra razón
        atexit.register(lambda: cleanup_and_close() if 'app' in locals() else None)
        
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n⚠️  Cerrado por usuario (Ctrl+C)")
    except Exception as e:
        print(f"❌ Error crítico al iniciar: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()