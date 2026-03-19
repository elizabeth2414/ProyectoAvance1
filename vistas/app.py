"""
Ventana Principal del Sistema de Gestion de Ventas (Versión Simplificada)
"""
import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from typing import Optional

from .componentes.sidebar import Sidebar
from .vista_productos import VistaProductos
from .vista_usuarios import VistaUsuarios

# Configurar tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppPrincipal(ctk.CTkToplevel):
    """Ventana principal de la aplicacion"""

    def __init__(
        self,
        conexion: sqlite3.Connection,
        usuario,
        on_logout: callable,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.conexion = conexion
        self.usuario = usuario
        self.on_logout_callback = on_logout
        self.vista_actual: Optional[ctk.CTkFrame] = None

        # Configuracion ventana
        self.title(f"Sistema de Ventas - {usuario.username}")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Centrar ventana
        self._centrar_ventana()

        # Manejar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self._cerrar_app)

        self._crear_layout()
        self._crear_barra_estado()

        # Mostrar productos por defecto
        self.sidebar.seleccionar("productos")

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        ancho = 1200
        alto = 700
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_layout(self):
        """Crea el layout principal"""
        # Configurar grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            usuario=self.usuario,
            on_navigate=self._navegar,
            on_logout=self._cerrar_sesion,
            fg_color=("#2b2b2b", "#1a1a1a")
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # Frame contenido
        self.frame_contenido = ctk.CTkFrame(self, corner_radius=0)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        self.frame_contenido.grid_rowconfigure(0, weight=1)

    def _crear_barra_estado(self):
        """Crea la barra de estado inferior"""
        self.barra_estado = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.barra_estado.grid(row=1, column=1, sticky="ew")

        # Conteos
        self.lbl_usuarios = ctk.CTkLabel(
            self.barra_estado,
            text="Usuarios: 0",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_usuarios.pack(side="left", padx=15)

        self.lbl_productos = ctk.CTkLabel(
            self.barra_estado,
            text="Productos: 0",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_productos.pack(side="left", padx=15)

        # Usuario y hora
        self.lbl_hora = ctk.CTkLabel(
            self.barra_estado,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_hora.pack(side="right", padx=15)

        self._actualizar_conteos()
        self._actualizar_hora()

    def _actualizar_conteos(self):
        """Actualiza los conteos en la barra de estado"""
        from controladores.producto_controller import ProductoController
        from controladores.usuario_controller import UsuarioController

        try:
            producto_ctrl = ProductoController(self.conexion)
            usuario_ctrl = UsuarioController(self.conexion)

            self.lbl_usuarios.configure(text=f"Usuarios: {usuario_ctrl.contar()}")
            self.lbl_productos.configure(text=f"Productos: {producto_ctrl.contar()}")
        except:
            pass

    def _actualizar_hora(self):
        """Actualiza la hora en la barra de estado"""
        hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lbl_hora.configure(text=hora_actual)
        self.after(1000, self._actualizar_hora)

    def _navegar(self, modulo: str):
        """Navega a un modulo especifico"""
        # Destruir vista actual
        if self.vista_actual:
            self.vista_actual.destroy()

        # Crear nueva vista
        if modulo == "productos":
            self.vista_actual = VistaProductos(
                self.frame_contenido,
                self.conexion,
                self.usuario
            )
        elif modulo == "usuarios":
            self.vista_actual = VistaUsuarios(
                self.frame_contenido,
                self.conexion,
                self.usuario
            )

        if self.vista_actual:
            self.vista_actual.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Actualizar conteos
        self._actualizar_conteos()

    def _cerrar_sesion(self):
        """Cierra la sesion actual"""
        if messagebox.askyesno("Cerrar Sesion", "Desea cerrar la sesion?"):
            self.destroy()
            self.on_logout_callback()

    def _cerrar_app(self):
        """Cierra la aplicacion completamente"""
        if messagebox.askyesno("Salir", "Desea salir del sistema?"):
            self.quit()
            self.destroy()

    def actualizar_vista(self):
        """Actualiza la vista actual"""
        if self.vista_actual and hasattr(self.vista_actual, 'actualizar'):
            self.vista_actual.actualizar()
        self._actualizar_conteos()
