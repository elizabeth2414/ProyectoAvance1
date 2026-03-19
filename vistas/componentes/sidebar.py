"""
Sidebar - Menu lateral reutilizable
"""
import customtkinter as ctk
from typing import Callable, Dict, Optional


class Sidebar(ctk.CTkFrame):
    """Menu lateral con navegacion"""

    def __init__(
        self,
        parent,
        usuario,
        on_navigate: Callable[[str], None],
        on_logout: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, width=200, corner_radius=0, **kwargs)

        self.usuario = usuario
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.botones: Dict[str, ctk.CTkButton] = {}
        self.boton_activo: Optional[str] = None

        self.grid_rowconfigure(13, weight=1)
        self.grid_propagate(False)

        self._crear_widgets()

    def _crear_widgets(self):
        """Crea los widgets del sidebar"""
        # Logo/Titulo
        self.lbl_logo = ctk.CTkLabel(
            self,
            text="Sistema de\nVentas",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3B8ED0"
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Separador
        self.sep1 = ctk.CTkFrame(self, height=2, fg_color="#3B8ED0")
        self.sep1.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Info usuario
        rol_texto = "Administrador" if self.usuario.es_admin() else "Cajero"
        self.lbl_usuario = ctk.CTkLabel(
            self,
            text=f"{self.usuario.username}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_usuario.grid(row=2, column=0, padx=20, pady=(10, 0))

        self.lbl_rol = ctk.CTkLabel(
            self,
            text=f"({rol_texto})",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_rol.grid(row=3, column=0, padx=20, pady=(0, 10))

        # Separador
        self.sep2 = ctk.CTkFrame(self, height=1, fg_color="gray50")
        self.sep2.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        # Botones de navegacion
        botones_config = [
            ("Usuarios", "usuarios", 5),
            ("Productos", "productos", 6),
        ]

        for texto, modulo, fila in botones_config:
            btn = ctk.CTkButton(
                self,
                text=texto,
                font=ctk.CTkFont(size=14),
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                command=lambda m=modulo: self._navegar(m)
            )
            btn.grid(row=fila, column=0, padx=10, pady=3, sticky="ew")
            self.botones[modulo] = btn

        # Boton cerrar sesion (abajo)
        self.btn_logout = ctk.CTkButton(
            self,
            text="Cerrar Sesion",
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=8,
            fg_color="#8B0000",
            hover_color="#A52A2A",
            command=self.on_logout
        )
        self.btn_logout.grid(row=8, column=0, padx=10, pady=(20, 20), sticky="ew")

    def _navegar(self, modulo: str):
        """Maneja la navegacion entre modulos"""
        # Resetear estilo del boton anterior
        if self.boton_activo and self.boton_activo in self.botones:
            self.botones[self.boton_activo].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )

        # Resaltar boton activo
        if modulo in self.botones:
            self.botones[modulo].configure(
                fg_color="#3B8ED0",
                text_color="white"
            )
            self.boton_activo = modulo

        self.on_navigate(modulo)

    def seleccionar(self, modulo: str):
        """Selecciona un modulo programaticamente"""
        self._navegar(modulo)
