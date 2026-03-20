"""Sidebar Material Design para navegacion principal."""

from PyQt6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from ..estilos import colores


class _NavButton(QPushButton):
    """Boton con animacion de desplazamiento para hover."""

    def __init__(self, texto: str, modulo: str, icono_nombre: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.modulo = modulo
        icono = qta.icon(icono_nombre, color="#D6E3FF", color_active="white")
        self.setIcon(icono)
        self.setIconSize(QSize(20, 20))
        self.setText(f"  {texto}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self._left_padding = 14
        self._activo = False
        self._animacion = QPropertyAnimation(self, b"minimumHeight", self)
        self._animacion.setDuration(140)
        self._animacion.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._base_style = ""
        self._actualizar_style(False)

    def _actualizar_style(self, activo: bool):
        if activo:
            self._base_style = (
                f"QPushButton {{"
                f"background-color: {colores.PRIMARY};"
                "color: white;"
                "border: none;"
                "border-left: 4px solid white;"
                f"padding: 10px 12px 10px {self._left_padding}px;"
                "text-align: left;"
                "border-radius: 8px;"
                "}"
            )
        else:
            self._base_style = (
                "QPushButton {"
                "background-color: transparent;"
                "color: #D6E3FF;"
                "border: none;"
                "border-left: 4px solid transparent;"
                f"padding: 10px 12px 10px {self._left_padding}px;"
                "text-align: left;"
                "border-radius: 8px;"
                "}"
                "QPushButton:hover { background-color: rgba(255, 255, 255, 0.08); }"
            )
        self.setStyleSheet(self._base_style)

    def set_activo(self, activo: bool):
        self._activo = activo
        self._actualizar_style(activo)

    def enterEvent(self, event: QEvent):
        self._left_padding = 18
        self._actualizar_style(self._activo)
        self._animacion.stop()
        self._animacion.setStartValue(self.minimumHeight())
        self._animacion.setEndValue(46)
        self._animacion.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self._left_padding = 14
        self._actualizar_style(self._activo)
        self._animacion.stop()
        self._animacion.setStartValue(self.minimumHeight())
        self._animacion.setEndValue(42)
        self._animacion.start()
        super().leaveEvent(event)


class Sidebar(QFrame):
    """Sidebar Material Design del sistema."""

    navegacion_cambiada = pyqtSignal(str)
    backup_solicitado = pyqtSignal()
    logout_solicitado = pyqtSignal()

    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        self.botones = {}
        self.boton_activo = ""
        self.setFixedWidth(220)
        self.setStyleSheet("QFrame { background-color: #1A1A2E; }")
        self._crear_ui()

    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)

        titulo = QLabel("📊 Sistema de Ventas")
        titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        titulo.setStyleSheet("color: white; padding: 4px 6px;")
        layout.addWidget(titulo)

        info = QFrame(self)
        info.setStyleSheet(
            "QFrame {"
            "background-color: rgba(255,255,255,0.06);"
            "border: 1px solid rgba(255,255,255,0.1);"
            "border-radius: 10px;"
            "}"
        )
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(6)

        avatar = QLabel(self._iniciales_usuario())
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(44, 44)
        avatar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        avatar.setStyleSheet(
            "QLabel {"
            f"background-color: {colores.PRIMARY};"
            "color: white;"
            "border-radius: 22px;"
            "}"
        )
        info_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        usuario_lbl = QLabel(self.usuario.username)
        usuario_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usuario_lbl.setStyleSheet("color: white; font-weight: 700;")
        info_layout.addWidget(usuario_lbl)

        rol = "Administrador" if self.usuario.es_admin() else "Cajero"
        rol_lbl = QLabel(rol)
        rol_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rol_lbl.setStyleSheet("color: #A9B8DA; font-size: 12px;")
        info_layout.addWidget(rol_lbl)
        layout.addWidget(info)

        for texto, modulo, icono in [
            ("Dashboard", "dashboard", "mdi6.view-dashboard"),
            ("Clientes", "clientes", "mdi6.account-group"),
            ("Productos", "productos", "mdi6.package-variant"),
            ("Proveedores", "proveedores", "fa6s.truck"),
            ("Ventas", "ventas", "mdi6.cart"),
            ("Reportes", "reportes", "mdi6.chart-bar"),
        ]:
            btn = _NavButton(texto, modulo, icono, self)
            btn.clicked.connect(lambda _, m=modulo: self.seleccionar(m))
            layout.addWidget(btn)
            self.botones[modulo] = btn

        separador = QFrame(self)
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("color: rgba(255,255,255,0.14);")
        layout.addWidget(separador)

        if self.usuario.es_admin():
            btn_backup = QPushButton("Backup")
            btn_backup.setProperty("variant", "success")
            btn_backup.setIcon(qta.icon("mdi6.database-export", color="white"))
            btn_backup.clicked.connect(self.backup_solicitado.emit)
            layout.addWidget(btn_backup)

        btn_logout = QPushButton("Cerrar Sesion")
        btn_logout.setProperty("variant", "danger")
        btn_logout.setIcon(qta.icon("mdi6.logout", color="white"))
        btn_logout.clicked.connect(self.logout_solicitado.emit)
        layout.addWidget(btn_logout)

        layout.addStretch(1)

    def _iniciales_usuario(self) -> str:
        texto = (self.usuario.username or "U").strip().upper()
        return (texto[:2] if texto else "U").ljust(2, "U")

    def seleccionar(self, modulo: str):
        for key, boton in self.botones.items():
            boton.set_activo(key == modulo)
        self.boton_activo = modulo
        self.navegacion_cambiada.emit(modulo)
