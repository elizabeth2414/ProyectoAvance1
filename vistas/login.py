"""Pantalla de login en PyQt6 con estilo Material Design."""

import sqlite3
from typing import Callable

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont
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

        panel_izq = QFrame()
        panel_izq.setStyleSheet(
            "QFrame {"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {colores.PRIMARY_DARK}, stop:1 {colores.PRIMARY});"
            "}"
        )
        izq_layout = QVBoxLayout(panel_izq)
        izq_layout.setContentsMargins(40, 50, 40, 50)
        izq_layout.setSpacing(16)

        logo = QLabel("🧾 Sistema de Gestion\nde Ventas")
        logo.setStyleSheet("color: white;")
        logo.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        izq_layout.addWidget(logo)

        descripcion = QLabel("Controla clientes, productos y ventas\nen una sola plataforma.")
        descripcion.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 14px;")
        descripcion.setWordWrap(True)
        izq_layout.addWidget(descripcion)
        izq_layout.addStretch(1)

        version = QLabel("Version 1.0")
        version.setStyleSheet("color: rgba(255, 255, 255, 0.75); font-size: 12px;")
        izq_layout.addWidget(version)

        panel_der = QFrame()
        der_layout = QVBoxLayout(panel_der)
        der_layout.setContentsMargins(70, 70, 70, 70)
        der_layout.setSpacing(14)

        titulo = QLabel("Bienvenido")
        titulo.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        der_layout.addWidget(titulo)

        subtitulo = QLabel("Ingresa tus credenciales")
        subtitulo.setStyleSheet(f"color: {colores.TEXT_SECONDARY}; font-size: 14px;")
        der_layout.addWidget(subtitulo)
        der_layout.addSpacing(12)

        self.input_usuario = self._crear_input("👤", "Usuario")
        der_layout.addWidget(self.input_usuario.parentWidget())

        self.input_password = self._crear_input("🔒", "Contrasena", password=True)
        der_layout.addWidget(self.input_password.parentWidget())

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {colores.DANGER}; font-size: 12px;")
        der_layout.addWidget(self.lbl_error)

        self.btn_login = QPushButton("Iniciar Sesion")
        self.btn_login.setProperty("variant", "primary")
        self.btn_login.setMinimumHeight(46)
        self.btn_login.setIcon(qta.icon("mdi6.login", color="white"))
        self.btn_login.setIconSize(QSize(20, 20))
        self.btn_login.clicked.connect(self._intentar_login)
        der_layout.addWidget(self.btn_login)
        der_layout.addStretch(1)

        contenedor.addWidget(panel_izq, 4)
        contenedor.addWidget(panel_der, 6)

        self.input_usuario.returnPressed.connect(self._intentar_login)
        self.input_password.returnPressed.connect(self._intentar_login)
        self.input_usuario.setFocus()

    def _crear_input(self, icono: str, placeholder: str, password: bool = False) -> QLineEdit:
        frame = QFrame(self)
        frame.setStyleSheet(f"QFrame {{ background-color: {colores.SURFACE}; border-radius: 10px; }}")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icono_lbl = QLabel()
        nombre_qta = "mdi6.account" if not password else "mdi6.lock"
        pixmap = qta.icon(nombre_qta, color="#B0B0B0").pixmap(QSize(20, 20))
        icono_lbl.setPixmap(pixmap)
        layout.addWidget(icono_lbl)

        input_text = QLineEdit()
        input_text.setPlaceholderText(placeholder)
        if password:
            input_text.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(input_text)
        if password:
            self.btn_eye = QPushButton()
            self.btn_eye.setIcon(qta.icon("mdi6.eye", color="#B0B0B0"))
            self.btn_eye.setIconSize(QSize(18, 18))
            self.btn_eye.setFlat(True)
            self.btn_eye.setStyleSheet(
                "QPushButton { background: transparent; border: none; }"
                "QPushButton:hover { color: white; }"
            )
            self.btn_eye.clicked.connect(self._toggle_password)
            layout.addWidget(self.btn_eye)
        return input_text

    def _toggle_password(self):
        self.password_visible = not self.password_visible
        self.input_password.setEchoMode(
            QLineEdit.EchoMode.Normal if self.password_visible else QLineEdit.EchoMode.Password
        )
        self.btn_eye.setIcon(
            qta.icon("mdi6.eye-off", color="white") if self.password_visible else qta.icon("mdi6.eye", color="white")
        )

    def _intentar_login(self):
        username = self.input_usuario.text().strip()
        password = self.input_password.text().strip()

        if not username:
            self.lbl_error.setText("Ingrese su nombre de usuario")
            self.input_usuario.setFocus()
            return
        if not password:
            self.lbl_error.setText("Ingrese su contrasena")
            self.input_password.setFocus()
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
            self.lbl_error.setText("Usuario o contrasena incorrectos")
            self.input_password.clear()
            self.input_password.setFocus()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar sesion:\n{exc}")

    def obtener_usuario(self):
        return self.usuario_logueado

    def limpiar_campos(self):
        self.input_usuario.clear()
        self.input_password.clear()
        self.lbl_error.clear()
        self.input_usuario.setFocus()
