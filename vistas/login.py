"""
Pantalla de login en PyQt6 con estilo moderno.
"""

import sqlite3
from typing import Callable

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from .estilos import colores
from .estilos.qss import get_global_stylesheet


class LoginWindow(QMainWindow):
    """Ventana principal de autenticacion."""

    login_exitoso = pyqtSignal(object)

    def __init__(self, conexion: sqlite3.Connection, on_login_success: Callable | None = None):
        super().__init__()
        self.conexion = conexion
        self.on_login_success = on_login_success
        self.usuario_logueado = None
        self.password_visible = False

        self.setWindowTitle("Sistema de Ventas - Login")
        self.setFixedSize(900, 600)
        self.setStyleSheet(get_global_stylesheet())
        self._centrar_ventana()
        self._crear_ui()

    def _centrar_ventana(self):
        screen = self.screen().availableGeometry() if self.screen() else self.geometry()
        x = screen.center().x() - self.width() // 2
        y = screen.center().y() - self.height() // 2
        self.move(x, y)

    def _crear_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        contenedor = QHBoxLayout(central)
        contenedor.setContentsMargins(0, 0, 0, 0)
        contenedor.setSpacing(0)

        # ── Panel izquierdo ──────────────────────────────────────────
        panel_izq = QFrame()
        panel_izq.setStyleSheet("QFrame { background-color: #1a1f3c; }")
        izq_layout = QVBoxLayout(panel_izq)
        izq_layout.setContentsMargins(40, 48, 40, 40)
        izq_layout.setSpacing(0)

        # Ícono
        icono_frame = QFrame()
        icono_frame.setFixedSize(46, 46)
        icono_frame.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; }"
        )

        icono_inner = QHBoxLayout(icono_frame)
        icono_inner.setContentsMargins(0, 0, 0, 0)

        icono_pix = QLabel()
        icono_pix.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono_pix.setPixmap(qta.icon("mdi6.receipt-text", color="white").pixmap(QSize(24, 24)))
        icono_inner.addWidget(icono_pix)

        izq_layout.addWidget(icono_frame)
        izq_layout.addSpacing(24)

        # Título
        logo = QLabel("Sistema de Gestión\nde Ventas")
        logo.setStyleSheet("color: white;")
        logo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        logo.setWordWrap(True)
        izq_layout.addWidget(logo)

        izq_layout.addSpacing(12)

        # Descripción
        descripcion = QLabel("Controla clientes, productos y ventas\nen una sola plataforma.")
        descripcion.setStyleSheet(
            "color: rgba(255, 255, 255, 0.55); font-size: 13px;"
        )
        descripcion.setWordWrap(True)
        izq_layout.addWidget(descripcion)

        izq_layout.addSpacing(24)

        # 🖼️ IMAGEN
        imagen = QLabel()
        imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("vistas/assets/store.png")  

        pixmap = pixmap.scaled(
            250, 250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        imagen.setPixmap(pixmap)

        izq_layout.addWidget(imagen)

        izq_layout.addSpacing(20)
        izq_layout.addStretch(1)

        # ── Panel derecho ────────────────────────────────────────────
        panel_der = QFrame()
        der_layout = QVBoxLayout(panel_der)
        der_layout.setContentsMargins(60, 0, 60, 0)
        der_layout.setSpacing(0)
        der_layout.addStretch(1)

        titulo = QLabel("Bienvenido de nuevo")
        titulo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        der_layout.addWidget(titulo)

        der_layout.addSpacing(4)

        subtitulo = QLabel("Ingresa tus credenciales para continuar")
        subtitulo.setStyleSheet(f"color: {colores.TEXT_SECONDARY}; font-size: 13px;")
        der_layout.addWidget(subtitulo)

        der_layout.addSpacing(28)

        # Usuario
        lbl_usuario = QLabel("Usuario")
        lbl_usuario.setStyleSheet(
            f"color: {colores.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        der_layout.addWidget(lbl_usuario)
        der_layout.addSpacing(6)

        self.input_usuario = self._crear_input("mdi6.account", "tu.usuario")
        der_layout.addWidget(self.input_usuario.parentWidget())

        der_layout.addSpacing(14)

        # Password
        lbl_password = QLabel("Contraseña")
        lbl_password.setStyleSheet(
            f"color: {colores.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        der_layout.addWidget(lbl_password)
        der_layout.addSpacing(6)

        self.input_password = self._crear_input("mdi6.lock", "••••••••", password=True)
        der_layout.addWidget(self.input_password.parentWidget())

        der_layout.addSpacing(20)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {colores.DANGER}; font-size: 12px;")
        der_layout.addWidget(self.lbl_error)

        der_layout.addSpacing(4)

        # Botón login
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setMinimumHeight(42)
        self.btn_login.setStyleSheet(
            "QPushButton { background-color: #4f46e5; color: white; border-radius: 8px; }"
            "QPushButton:hover { background-color: #4338ca; }"
        )
        self.btn_login.setIcon(qta.icon("mdi6.login", color="white"))
        self.btn_login.setIconSize(QSize(18, 18))
        self.btn_login.clicked.connect(self._intentar_login)
        der_layout.addWidget(self.btn_login)

        der_layout.addStretch(1)

        contenedor.addWidget(panel_izq, 4)
        contenedor.addWidget(panel_der, 6)

        self.input_usuario.returnPressed.connect(self._intentar_login)
        self.input_password.returnPressed.connect(self._intentar_login)
        self.input_usuario.setFocus()

    def _crear_input(self, nombre_qta: str, placeholder: str, password: bool = False) -> QLineEdit:
        frame = QFrame(self)
        frame.setFixedHeight(42)
        frame.setStyleSheet(
            f"QFrame {{ background-color: {colores.SURFACE}; border-radius: 8px; }}"
        )

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 0, 12, 0)

        icono_lbl = QLabel()
        icono_lbl.setPixmap(qta.icon(nombre_qta, color="#B0B0B0").pixmap(QSize(18, 18)))
        layout.addWidget(icono_lbl)

        input_text = QLineEdit()
        input_text.setPlaceholderText(placeholder)
        input_text.setStyleSheet("border: none; background: transparent;")
        if password:
            input_text.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(input_text)

        if password:
            self.btn_eye = QPushButton()
            self.btn_eye.setIcon(qta.icon("mdi6.eye", color="#B0B0B0"))
            self.btn_eye.setFlat(True)
            self.btn_eye.clicked.connect(self._toggle_password)
            layout.addWidget(self.btn_eye)

        return input_text

    def _toggle_password(self):
        self.password_visible = not self.password_visible
        self.input_password.setEchoMode(
            QLineEdit.EchoMode.Normal if self.password_visible else QLineEdit.EchoMode.Password
        )

    def _intentar_login(self):
        username = self.input_usuario.text().strip()
        password = self.input_password.text().strip()

        if not username:
            self.lbl_error.setText("Ingrese su nombre de usuario")
            return
        if not password:
            self.lbl_error.setText("Ingrese su contraseña")
            return

        from controladores.usuario_controller import UsuarioController
        from modelos.excepciones import CredencialesInvalidasError

        try:
            usuario = UsuarioController(self.conexion).autenticar(username, password)
            self.usuario_logueado = usuario
            self.lbl_error.setText("")
            self.login_exitoso.emit(usuario)

            if self.on_login_success:
                self.on_login_success(usuario)

        except CredencialesInvalidasError:
            self.lbl_error.setText("Usuario o contraseña incorrectos")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def obtener_usuario(self):
        return self.usuario_logueado
    