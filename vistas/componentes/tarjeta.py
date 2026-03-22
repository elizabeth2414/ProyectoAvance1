"""Tarjeta de resumen con estilo Material Design y animaciones avanzadas."""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QSizePolicy, QVBoxLayout
import qtawesome as qta

from ..estilos import colores


def _oscurecer_color(color_hex: str, factor: float = 0.3) -> str:
    """Oscurece un color hex multiplicando sus componentes RGB."""
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    return f'#{r:02x}{g:02x}{b:02x}'


class TarjetaResumen(QFrame):
    """Tarjeta con titulo, valor y acento de color con animaciones avanzadas."""

    def __init__(self, parent, titulo: str, valor: str, color: str, icono_nombre: str | None = None):
        super().__init__(parent)
        self._base_geometry = QRect()
        self._hover_activo = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(130)
        self.setMaximumHeight(180)

        self.color_acento = color
        self.setProperty("class", "card")
        
        # Calcular color de fondo basado en el acento (más colorido)
        color_fondo = _oscurecer_color(color, 0.28)
        color_borde = _oscurecer_color(color, 0.35)
        
        self.setStyleSheet(
            "QFrame {"
            f"background-color: {color_fondo};"
            "border-radius: 12px;"
            f"border: 1px solid {color_borde};"
            "}"
        )

        # Sombra mejorada
        self.sombra = QGraphicsDropShadowEffect(self)
        self.sombra.setBlurRadius(20)
        self.sombra.setOffset(0, 4)
        self.sombra.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.sombra)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # Barra de acento animada
        self.barra = QFrame(self)
        self.barra.setFixedHeight(4)
        self.barra.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 2px; }}")
        layout.addWidget(self.barra)

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
            self.icono_pixmap = qta.icon(icono_nombre, color=color).pixmap(QSize(36, 36))
            icono_lbl.setPixmap(self.icono_pixmap)
            self.icono_label = icono_lbl
            layout.addWidget(icono_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addStretch(1)

        # Animaciones
        self._anim_scale = QPropertyAnimation(self, b"geometry", self)
        self._anim_scale.setDuration(200)
        self._anim_scale.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Animación de sombra
        self._anim_shadow = QPropertyAnimation(self.sombra, b"blurRadius", self)
        self._anim_shadow.setDuration(200)
        self._anim_shadow.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        """Efectos al pasar mouse sobre la tarjeta."""
        self._hover_activo = True
        self._animar_escala(1.04)
        
        # Aumentar sombra
        self._anim_shadow.stop()
        self._anim_shadow.setStartValue(self.sombra.blurRadius())
        self._anim_shadow.setEndValue(35)
        self._anim_shadow.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Volver a estado normal cuando se sale el mouse."""
        self._hover_activo = False
        self._animar_escala(1.0)
        
        # Reducir sombra
        self._anim_shadow.stop()
        self._anim_shadow.setStartValue(self.sombra.blurRadius())
        self._anim_shadow.setEndValue(20)
        self._anim_shadow.start()
        
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
        self._anim_scale.stop()
        self._anim_scale.setStartValue(self.geometry())
        self._anim_scale.setEndValue(destino)
        self._anim_scale.start()

    def actualizar_valor(self, valor: str):
        """Actualiza el valor con animación de cambio suave."""
        # Desvanecer valor anterior
        self.lbl_valor.setStyleSheet(
            f"color: {colores.TEXT_PRIMARY}; opacity: 0.5;"
        )
        
        # Cambiar valor
        self.lbl_valor.setText(str(valor))
        
        # Re-aparecer
        self.lbl_valor.setStyleSheet(
            f"color: {colores.TEXT_PRIMARY};"
        )
