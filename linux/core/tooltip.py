#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToolTip reutilizable para widgets de CustomTkinter / Tkinter
Compatible con cualquier versión de customtkinter.
"""

import customtkinter as ctk
from typing import Any, Optional


class ToolTip:
    """
    Muestra un tooltip emergente al pasar el mouse sobre un widget.
    
    Uso:
        ToolTip(mi_boton, "Texto de ayuda", delay=0.4)
    """
    
    def __init__(
        self, 
        widget: Any, 
        text: str, 
        delay: float = 0.4, 
        alpha: float = 0.95, 
        **style_kwargs
    ):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.alpha = alpha
        
        # Estilos por defecto + personalizables
        self._style = {
            "font_size": 11,
            "fg_color": "#2C2C2C",
            "text_color": "#FFFFFF",
            "corner_radius": 8,
            "padx": 12,
            "pady": 6,
        }
        self._style.update(style_kwargs)
        
        self._tooltip_window: Optional[ctk.CTkToplevel] = None
        self._after_id: Optional[str] = None
        
        # Bindings seguros (add="+" para no sobrescribir otros eventos)
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None) -> None:
        self._schedule()

    def _on_leave(self, event=None) -> None:
        self._unschedule()
        self._hide_tooltip()

    def _schedule(self) -> None:
        self._unschedule()
        self._after_id = self.widget.after(int(self.delay * 1000), self._show_tooltip)

    def _unschedule(self) -> None:
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show_tooltip(self) -> None:
        if self._tooltip_window or not self.widget.winfo_exists():
            return

        # Posición inicial (debajo y ligeramente a la derecha del widget)
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

        # Crear ventana flotante
        self._tooltip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)  # Sin bordes ni barra de título
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-alpha", self.alpha)

        # Label con estilos
        label = ctk.CTkLabel(
            tw,
            text=self.text,
            font=ctk.CTkFont(size=self._style["font_size"], weight="normal"),
            fg_color=self._style["fg_color"],
            text_color=self._style["text_color"],
            corner_radius=self._style["corner_radius"],
            padx=self._style["padx"],
            pady=self._style["pady"]
        )
        label.pack()

        # Ajuste de límites de pantalla
        tw.update_idletasks()
        tw_w = tw.winfo_width()
        screen_w = self.widget.winfo_screenwidth()
        if x + tw_w > screen_w:
            x = screen_w - tw_w - 10
            tw.wm_geometry(f"+{x}+{y}")

    def _hide_tooltip(self) -> None:
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None