"""
Pantalla de Login del Sistema de Gestion de Ventas
"""
import customtkinter as ctk
from typing import Optional, Callable
import sqlite3

# Configurar tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """Ventana de inicio de sesion"""

    def __init__(
        self,
        conexion: sqlite3.Connection,
        on_login_success: Callable,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.conexion = conexion
        self.on_login_success = on_login_success
        self.usuario_logueado = None

        # Configuracion ventana
        self.title("Sistema de Ventas - Login")
        self.geometry("450x620")
        self.resizable(False, False)

        # Centrar ventana
        self._centrar_ventana()

        self._crear_widgets()

        # Bind Enter key
        self.bind("<Return>", lambda e: self._intentar_login())

    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        ancho = 450
        alto = 620
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_widgets(self):
        """Crea los widgets de la ventana"""
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self, corner_radius=0)
        self.frame_principal.pack(fill="both", expand=True)

        # Logo/Titulo
        self.frame_logo = ctk.CTkFrame(
            self.frame_principal,
            fg_color="#1f538d",
            height=150,
            corner_radius=0
        )
        self.frame_logo.pack(fill="x")
        self.frame_logo.pack_propagate(False)

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_logo,
            text="Sistema de\nGestion de Ventas",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        self.lbl_titulo.place(relx=0.5, rely=0.5, anchor="center")

        # Frame formulario
        self.frame_form = ctk.CTkFrame(
            self.frame_principal,
            fg_color="transparent"
        )
        self.frame_form.pack(fill="both", expand=True, padx=30, pady=20)

        # Titulo login
        self.lbl_login = ctk.CTkLabel(
            self.frame_form,
            text="Iniciar Sesion",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_login.pack(pady=(10, 15))

        # Campo usuario
        self.lbl_usuario = ctk.CTkLabel(
            self.frame_form,
            text="Usuario",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.lbl_usuario.pack(fill="x")

        self.entry_usuario = ctk.CTkEntry(
            self.frame_form,
            height=45,
            font=ctk.CTkFont(size=14),
            placeholder_text="Ingrese su usuario"
        )
        self.entry_usuario.pack(fill="x", pady=(5, 15))

        # Campo password
        self.lbl_password = ctk.CTkLabel(
            self.frame_form,
            text="Contrasena",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.lbl_password.pack(fill="x")

        self.entry_password = ctk.CTkEntry(
            self.frame_form,
            height=45,
            font=ctk.CTkFont(size=14),
            placeholder_text="Ingrese su contrasena",
            show="*"
        )
        self.entry_password.pack(fill="x", pady=(5, 8))

        # Checkbox mostrar password
        self.var_mostrar = ctk.BooleanVar(value=False)
        self.chk_mostrar = ctk.CTkCheckBox(
            self.frame_form,
            text="Mostrar contrasena",
            variable=self.var_mostrar,
            command=self._toggle_password,
            font=ctk.CTkFont(size=12)
        )
        self.chk_mostrar.pack(anchor="w", pady=(0, 12))

        # Label error
        self.lbl_error = ctk.CTkLabel(
            self.frame_form,
            text="",
            text_color="#FF6B6B",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_error.pack(fill="x", pady=(0, 8))

        # Boton login
        self.btn_login = ctk.CTkButton(
            self.frame_form,
            text="Iniciar Sesion",
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._intentar_login
        )
        self.btn_login.pack(fill="x", pady=(5, 10))

        # Footer
        self.lbl_footer = ctk.CTkLabel(
            self.frame_principal,
            text="Sistema de Gestion de Ventas v1.0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_footer.pack(side="bottom", pady=10)

        # Focus inicial
        self.entry_usuario.focus_set()

    def _toggle_password(self):
        """Muestra u oculta la contrasena"""
        if self.var_mostrar.get():
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")

    def _intentar_login(self):
        """Intenta autenticar al usuario"""
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        # Validaciones
        if not username:
            self.lbl_error.configure(text="Ingrese su nombre de usuario")
            self.entry_usuario.focus_set()
            return

        if not password:
            self.lbl_error.configure(text="Ingrese su contrasena")
            self.entry_password.focus_set()
            return

        # Importar controlador
        from controladores.usuario_controller import UsuarioController
        from modelos.excepciones import CredencialesInvalidasError

        try:
            usuario_ctrl = UsuarioController(self.conexion)
            usuario = usuario_ctrl.autenticar(username, password)

            self.usuario_logueado = usuario
            self.lbl_error.configure(text="")

            # Llamar callback de exito
            self.on_login_success(usuario)

        except CredencialesInvalidasError:
            self.lbl_error.configure(text="Usuario o contrasena incorrectos")
            self.entry_password.delete(0, "end")
            self.entry_password.focus_set()

        except Exception as e:
            self.lbl_error.configure(text=f"Error: {str(e)}")

    def obtener_usuario(self):
        """Retorna el usuario logueado"""
        return self.usuario_logueado
