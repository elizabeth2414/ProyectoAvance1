"""Tarjeta de resumen con estilo Material Design."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QSizePolicy, QVBoxLayout
import qtawesome as qta

from ..estilos import colores


class TarjetaResumen(QFrame):
    """Tarjeta con titulo, valor y acento de color."""

    def __init__(self, parent, titulo: str, valor: str, color: str, icono_nombre: str | None = None):
        super().__init__(parent)
        self._base_geometry = QRect()
        self._hover_activo = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(130)
        self.setMaximumHeight(180)

        self.setProperty("class", "card")
        self.setStyleSheet(
            "QFrame {"
            f"background-color: {colores.SURFACE};"
            "border-radius: 12px;"
            "border: 1px solid #2A2A2A;"
            "}"
        )

        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(24)
        sombra.setOffset(0, 6)
        sombra.setColor(sombra.color().fromRgb(0, 0, 0, 140))
        self.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        barra = QFrame(self)
        barra.setFixedHeight(4)
        barra.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 2px; }}")
        layout.addWidget(barra)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        lbl_titulo.setStyleSheet(f"color: {colores.TEXT_SECONDARY};")
        layout.addWidget(lbl_titulo)

        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.lbl_valor.setStyleSheet(f"color: {colores.TEXT_PRIMARY};")
        layout.addWidget(self.lbl_valor)

        if icono_nombre:
            icono_lbl = QLabel()
            pixmap = qta.icon(icono_nombre, color=color).pixmap(QSize(36, 36))
            icono_lbl.setPixmap(pixmap)
            layout.addWidget(icono_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addStretch(1)

        self._animacion = QPropertyAnimation(self, b"geometry", self)
        self._animacion.setDuration(160)
        self._animacion.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self._hover_activo = True
        self._animar_escala(1.02)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_activo = False
        self._animar_escala(1.0)
        super().leaveEvent(event)

    def showEvent(self, event):
        self._base_geometry = self.geometry()
        super().showEvent(event)

    def _animar_escala(self, factor: float):
        if self._base_geometry.isNull():
            self._base_geometry = self.geometry()
        base = self._base_geometry
        if factor > 1.0:
            delta_w = int(base.width() * (factor - 1.0) / 2)
            delta_h = int(base.height() * (factor - 1.0) / 2)
            destino = QRect(
                base.x() - delta_w,
                base.y() - delta_h,
                base.width() + (delta_w * 2),
                base.height() + (delta_h * 2),
            )
        else:
            destino = base
        self._animacion.stop()
        self._animacion.setStartValue(self.geometry())
        self._animacion.setEndValue(destino)
        self._animacion.start()

    def actualizar_valor(self, valor: str):
        self.lbl_valor.setText(str(valor))
