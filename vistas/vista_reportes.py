"""Vista de reportes y gráficos con matplotlib embebido en PyQt6."""

import sqlite3
from datetime import datetime, timedelta
import numpy as np

from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

from controladores.venta_controller import VentaController
from vistas.estilos.colores import (
    PRIMARY,
    SUCCESS,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


PALETA = ["#1565C0", "#2E7D32", "#F57F17", "#C62828", "#7B1FA2"]


def _crear_titulo(icono_nombre: str, texto: str, color_icono: str = "#FFFFFF") -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    icono_lbl = QLabel()
    pixmap = qta.icon(icono_nombre, color=color_icono).pixmap(QSize(32, 32))
    icono_lbl.setPixmap(pixmap)

    titulo_lbl = QLabel(texto)
    titulo_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))

    layout.addWidget(icono_lbl)
    layout.addWidget(titulo_lbl)
    layout.addStretch(1)
    return widget


def _aplicar_estilo_boton(btn: QPushButton, clase: str):
    btn.setProperty("class", clase)
    btn.style().unpolish(btn)
    btn.style().polish(btn)


def _msg(parent, icon: QMessageBox.Icon, title: str, text: str):
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStyleSheet(f"background-color: {SURFACE}; color: {TEXT_PRIMARY};")
    msg.exec()


class VistaReportes(QWidget):
    """Reportes visuales con 4 tipos de gráfico."""

    def __init__(self, parent, conexion: sqlite3.Connection, usuario):
        super().__init__(parent)
        self.conexion = conexion
        self.usuario = usuario
        self.venta_ctrl = VentaController(conexion)

        self._crear_ui()
        self.generar_reporte()

    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(_crear_titulo("mdi6.chart-bar", "Reportes y Gráficos", PRIMARY))

        panel = QFrame(self)
        panel.setProperty("class", "card")
        controls = QHBoxLayout(panel)

        self.combo_tipo = QComboBox(self)
        self.combo_tipo.addItems(
            [
                "Ventas por Día",
                "Ventas por Mes",
                "Top 5 Productos más vendidos",
                "Ventas por Categoría",
            ]
        )
        self.combo_tipo.currentTextChanged.connect(self.generar_reporte)

        self.input_inicio = QLineEdit((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.input_fin = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        
        lbl_inicio = QLabel("Desde:")
        lbl_fin = QLabel("Hasta:")

        btn_generar = QPushButton("Generar Reporte")
        _aplicar_estilo_boton(btn_generar, "btn-success")
        btn_generar.clicked.connect(self.generar_reporte)

        btn_exportar = QPushButton("Exportar PNG")
        _aplicar_estilo_boton(btn_exportar, "btn-primary")
        btn_exportar.clicked.connect(self.exportar_png)

        controls.addWidget(self.combo_tipo, 2)
        controls.addWidget(lbl_inicio)
        controls.addWidget(self.input_inicio)
        controls.addWidget(lbl_fin)
        controls.addWidget(self.input_fin)
        controls.addWidget(btn_generar)
        controls.addWidget(btn_exportar)
        layout.addWidget(panel)

        grafico_frame = QFrame(self)
        grafico_frame.setProperty("class", "card")
        grafico_layout = QVBoxLayout(grafico_frame)

        self.figure = Figure(facecolor="#1E1E1E", constrained_layout=False)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        grafico_layout.addWidget(self.canvas)
        layout.addWidget(grafico_frame, 1)

    def generar_reporte(self):
        """Genera el reporte según el tipo seleccionado y las fechas"""
        tipo = self.combo_tipo.currentText()
        try:
            if tipo == "Ventas por Día":
                self._grafico_ventas_dia()
            elif tipo == "Ventas por Mes":
                self._grafico_ventas_mes()
            elif tipo == "Top 5 Productos más vendidos":
                self._grafico_top_productos()
            else:
                self._grafico_ventas_categoria()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _estilo_axes(self, titulo: str):
        """Aplica estilos a los ejes del gráfico"""
        self.figure.patch.set_facecolor("#1E1E1E")
        self.ax.set_facecolor("#1E1E1E")
        self.ax.set_title(titulo, color=TEXT_PRIMARY, fontsize=13, fontweight="bold")
        self.ax.tick_params(colors=TEXT_PRIMARY)
        self.ax.xaxis.label.set_color(TEXT_PRIMARY)
        self.ax.yaxis.label.set_color(TEXT_PRIMARY)
        for sp in self.ax.spines.values():
            sp.set_color(TEXT_SECONDARY)

    def _limpiar_figura(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

    def _sin_datos(self):
        self._limpiar_figura()
        self._estilo_axes("Sin datos")
        self.ax.text(0.5, 0.5, "No hay datos disponibles", ha="center", va="center", color=TEXT_SECONDARY)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def _grafico_ventas_dia(self):
        fi = self.input_inicio.text().strip()
        ff = self.input_fin.text().strip()
        try:
            datetime.strptime(fi, "%Y-%m-%d")
            datetime.strptime(ff, "%Y-%m-%d")
        except ValueError:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        datos = self.venta_ctrl.ventas_por_dia(fi, ff)
        if not datos:
            self._sin_datos()
            return

        x = [d[0] for d in datos]
        y = [float(d[1]) for d in datos]
        self._limpiar_figura()
        self._estilo_axes(f"Ventas por Día ({fi} a {ff})")
        
        # Crear barras con altura inicial 0
        bars = self.ax.bar(x, [0] * len(y), color=PRIMARY, edgecolor=TEXT_PRIMARY, linewidth=1.5)
        self.ax.set_ylabel("Monto S/", color=TEXT_PRIMARY)
        self.ax.set_xlabel("Fecha", color=TEXT_PRIMARY)
        self.ax.set_ylim(0, max(y) * 1.1 if max(y) > 0 else 1)
        
        if len(x) > 10:
            self.ax.tick_params(axis="x", rotation=45)
        
        self.ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Animación de crecimiento de barras
        self._animar_barras(bars, y, x)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _animar_barras(self, bars, valores, etiquetas):
        """Anima el crecimiento de las barras."""
        max_frames = 30
        
        def actualizar_frame(frame):
            progreso = frame / max_frames
            for bar, valor in zip(bars, valores):
                bar.set_height(valor * progreso)
            self.canvas.draw_idle()
        
        # Usar timer para animar
        self.frame_actual = 0
        self.timer_anim = QTimer(self)
        
        def on_timer():
            if self.frame_actual <= max_frames:
                actualizar_frame(self.frame_actual)
                
                # Agregar texto sobre barras en el último frame
                if self.frame_actual == max_frames:
                    for bar, v in zip(bars, valores):
                        if v > 0:
                            self.ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
                                       f"S/{v:.0f}", ha="center", va="bottom", color=SUCCESS, fontsize=9, fontweight='bold')
                    self.canvas.draw()
                
                self.frame_actual += 1
            else:
                self.timer_anim.stop()
        
        self.timer_anim.timeout.connect(on_timer)
        self.timer_anim.start(16)  # ~60 FPS

    def _grafico_ventas_mes(self):
        fi = self.input_inicio.text().strip()
        ff = self.input_fin.text().strip()
        try:
            datetime.strptime(fi, "%Y-%m-%d")
            datetime.strptime(ff, "%Y-%m-%d")
        except ValueError:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        datos = self.venta_ctrl.ventas_por_mes(datetime.now().year, fi, ff)
        if not datos:
            self._sin_datos()
            return
        
        x = [d[0] for d in datos]
        y = [float(d[1]) for d in datos]
        self._limpiar_figura()
        self._estilo_axes(f"Ventas por Mes ({fi} a {ff})")
        colores = ["#1565C0", "#1976D2", "#1E88E5", "#2196F3", "#42A5F5", "#64B5F6"]
        
        # Crear barras con altura inicial 0
        bars = self.ax.bar(x, [0] * len(y), color=colores[: len(x)], edgecolor=TEXT_PRIMARY, linewidth=1.5)
        self.ax.set_ylabel("Monto S/", color=TEXT_PRIMARY)
        self.ax.set_xlabel("Período", color=TEXT_PRIMARY)
        self.ax.set_ylim(0, max(y) * 1.1 if max(y) > 0 else 1)
        
        self.ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Animación de crecimiento
        self._animar_barras_mes(bars, y)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _animar_barras_mes(self, bars, valores):
        """Anima el crecimiento de las barras de mes."""
        max_frames = 30
        
        def actualizar_frame(frame):
            progreso = frame / max_frames
            for bar, valor in zip(bars, valores):
                bar.set_height(valor * progreso)
            self.canvas.draw_idle()
        
        self.frame_actual = 0
        self.timer_anim = QTimer(self)
        
        def on_timer():
            if self.frame_actual <= max_frames:
                actualizar_frame(self.frame_actual)
                
                if self.frame_actual == max_frames:
                    for b, v in zip(bars, valores):
                        if v > 0:
                            self.ax.text(b.get_x() + b.get_width() / 2, b.get_height(), 
                                       f"S/{v:.0f}", ha="center", va="bottom", color=SUCCESS, fontsize=10, fontweight='bold')
                    self.canvas.draw()
                
                self.frame_actual += 1
            else:
                self.timer_anim.stop()
        
        self.timer_anim.timeout.connect(on_timer)
        self.timer_anim.start(16)

    def _grafico_top_productos(self):
        fi = self.input_inicio.text().strip()
        ff = self.input_fin.text().strip()
        try:
            datetime.strptime(fi, "%Y-%m-%d")
            datetime.strptime(ff, "%Y-%m-%d")
        except ValueError:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        datos = self.venta_ctrl.top_productos(5, fi, ff)
        if not datos:
            self._sin_datos()
            return
        
        ylabels = [d[0][:25] for d in datos]
        vals = [float(d[1]) for d in datos]
        self._limpiar_figura()
        self._estilo_axes(f"Top 5 Productos ({fi} a {ff})")
        colors = PALETA[: len(vals)]
        
        # Crear barras con ancho inicial 0
        bars = self.ax.barh(ylabels, [0] * len(vals), color=colors, edgecolor=TEXT_PRIMARY, linewidth=1.5)
        self.ax.set_xlabel("Cantidad vendida", color=TEXT_PRIMARY)
        self.ax.set_xlim(0, max(vals) * 1.1 if max(vals) > 0 else 1)
        self.ax.invert_yaxis()
        
        self.ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Animación de crecimiento
        self._animar_barras_h(bars, vals)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _animar_barras_h(self, bars, valores):
        """Anima el crecimiento de las barras horizontales."""
        max_frames = 30
        
        def actualizar_frame(frame):
            progreso = frame / max_frames
            for bar, valor in zip(bars, valores):
                bar.set_width(valor * progreso)
            self.canvas.draw_idle()
        
        self.frame_actual = 0
        self.timer_anim = QTimer(self)
        
        def on_timer():
            if self.frame_actual <= max_frames:
                actualizar_frame(self.frame_actual)
                
                if self.frame_actual == max_frames:
                    for b, v in zip(bars, valores):
                        if v > 0:
                            self.ax.text(v, b.get_y() + b.get_height() / 2, f"  {v:.0f} unid.", 
                                       va="center", color=SUCCESS, fontsize=10, fontweight='bold')
                    self.canvas.draw()
                
                self.frame_actual += 1
            else:
                self.timer_anim.stop()
        
        self.timer_anim.timeout.connect(on_timer)
        self.timer_anim.start(16)

    def _grafico_ventas_categoria(self):
        fi = self.input_inicio.text().strip()
        ff = self.input_fin.text().strip()
        try:
            datetime.strptime(fi, "%Y-%m-%d")
            datetime.strptime(ff, "%Y-%m-%d")
        except ValueError:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        datos = self.venta_ctrl.ventas_por_categoria(fi, ff)
        if not datos:
            self._sin_datos()
            return

        labels = [d[0] for d in datos]
        vals = [float(d[1]) for d in datos]

        self._limpiar_figura()

        # Crear gráfico de pastel
        self.ax = self.figure.add_subplot(111)
        self._estilo_axes(f"Ventas por Categoría ({fi} a {ff})")

        explode = [0.05] * len(vals)
        colores = PALETA[:len(vals)]

        # Crear el pastel
        wedges, texts, autotexts = self.ax.pie(
            vals,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colores,
            explode=explode,
            pctdistance=0.85,
            wedgeprops={"linewidth": 2, "edgecolor": "#1E1E1E"},
            shadow=True,
        )

        # Estilo de etiquetas
        for text in texts:
            text.set_color(TEXT_PRIMARY)
            text.set_fontsize(10)
            text.set_fontweight('bold')

        # Estilo de porcentajes
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")

        self.figure.tight_layout()
        self.canvas.draw()

    def _animar_pie(self, ax, angulo_inicio, angulo_fin, duracion_frames):
        """Animación de pastel deshabilitada (no compatible con matplotlib)."""
        pass

    def exportar_png(self):
        dialog = QFileDialog(self)
        dialog.setStyleSheet(f"background-color: {SURFACE}; color: {TEXT_PRIMARY};")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilters(["Imagen PNG (*.png)"])
        dialog.selectFile(f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        if dialog.exec() != QFileDialog.DialogCode.Accepted:
            return
        ruta = dialog.selectedFiles()[0]
        try:
            self.figure.savefig(ruta, dpi=150, facecolor="#1E1E1E")
            _msg(self, QMessageBox.Icon.Information, "Éxito", f"Reporte exportado en:\n{ruta}")
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def actualizar(self):
        self.generar_reporte()
