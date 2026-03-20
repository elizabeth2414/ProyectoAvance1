"""Vista de reportes y gráficos con matplotlib embebido en PyQt6."""

import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtCore import QSize
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
        self._toggle_fechas()
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
                "Ventas por Día (últimos 30 días)",
                "Ventas por Mes (año actual)",
                "Top 5 Productos más vendidos",
                "Ventas por Categoría",
            ]
        )
        self.combo_tipo.currentTextChanged.connect(self._toggle_fechas)

        self.input_inicio = QLineEdit((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.input_fin = QLineEdit(datetime.now().strftime("%Y-%m-%d"))

        btn_generar = QPushButton("Generar Reporte")
        _aplicar_estilo_boton(btn_generar, "btn-success")
        btn_generar.clicked.connect(self.generar_reporte)

        btn_exportar = QPushButton("Exportar PNG")
        _aplicar_estilo_boton(btn_exportar, "btn-primary")
        btn_exportar.clicked.connect(self.exportar_png)

        controls.addWidget(self.combo_tipo, 2)
        controls.addWidget(self.input_inicio)
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

    def _toggle_fechas(self):
        es_dia = self.combo_tipo.currentText() == "Ventas por Día (últimos 30 días)"
        self.input_inicio.setEnabled(es_dia)
        self.input_fin.setEnabled(es_dia)

    def _estilo_axes(self, titulo: str):
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

    def generar_reporte(self):
        tipo = self.combo_tipo.currentText()
        try:
            if tipo == "Ventas por Día (últimos 30 días)":
                self._grafico_ventas_dia()
            elif tipo == "Ventas por Mes (año actual)":
                self._grafico_ventas_mes()
            elif tipo == "Top 5 Productos más vendidos":
                self._grafico_top_productos()
            else:
                self._grafico_ventas_categoria()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

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
        self._estilo_axes("Ventas por Día")
        bars = self.ax.bar(x, y, color=PRIMARY)
        self.ax.set_ylabel("Monto S/")
        if len(x) > 10:
            self.ax.tick_params(axis="x", rotation=45)
        for b, v in zip(bars, y):
            self.ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{v:.0f}", ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=8)
        self.canvas.draw()

    def _grafico_ventas_mes(self):
        datos = self.venta_ctrl.ventas_por_mes(datetime.now().year)
        x = [d[0] for d in datos]
        y = [float(d[1]) for d in datos]
        self._limpiar_figura()
        self._estilo_axes("Ventas por Mes")
        colores = ["#0D47A1", "#1565C0", "#1976D2", "#1E88E5", "#2196F3", "#42A5F5", "#64B5F6", "#90CAF9", "#BBDEFB", "#64B5F6", "#1E88E5", "#1565C0"]
        bars = self.ax.bar(x, y, color=colores[: len(x)])
        self.ax.set_ylabel("Monto S/")
        for b, v in zip(bars, y):
            if v > 0:
                self.ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{v:.0f}", ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=8)
        self.canvas.draw()

    def _grafico_top_productos(self):
        datos = self.venta_ctrl.top_productos(5)
        if not datos:
            self._sin_datos()
            return
        ylabels = [d[0] for d in datos]
        vals = [float(d[1]) for d in datos]
        self._limpiar_figura()
        self._estilo_axes("Top 5 Productos más vendidos")
        bars = self.ax.barh(ylabels, vals, color=PALETA[: len(vals)])
        self.ax.set_xlabel("Cantidad vendida")
        self.ax.invert_yaxis()
        for b, v in zip(bars, vals):
            self.ax.text(v, b.get_y() + b.get_height() / 2, f" {v:.0f}", va="center", color=TEXT_PRIMARY)
        self.canvas.draw()

    def _grafico_ventas_categoria(self):
        datos = self.venta_ctrl.ventas_por_categoria()
        if not datos:
            self._sin_datos()
            return

        labels = [d[0] for d in datos]
        vals = [float(d[1]) for d in datos]

        self._limpiar_figura()

        # Usar subplots con espacio para leyenda
        self.ax = self.figure.add_subplot(111)
        self._estilo_axes("Ventas por Categoría")

        explode = [0.03] * len(vals)
        colores = PALETA[:len(vals)]

        wedges, texts, autotexts = self.ax.pie(
            vals,
            autopct="%1.1f%%",
            startangle=90,
            colors=colores,
            explode=explode,
            pctdistance=0.75,
            labeldistance=None,
            wedgeprops={"linewidth": 2, "edgecolor": "#1E1E1E"},
        )

        # Estilo de porcentajes
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(10)
            autotext.set_fontweight("bold")

        # Leyenda externa con montos formateada
        leyenda_labels = [f"{l}  —  S/ {v:,.2f}" for l, v in zip(labels, vals)]

        self.ax.legend(
            wedges,
            leyenda_labels,
            loc="center left",
            bbox_to_anchor=(1.05, 0.5),
            frameon=True,
            facecolor="#2D2D2D",
            edgecolor="#3D3D3D",
            labelcolor="#FFFFFF",
            fontsize=10,
            borderpad=1,
            labelspacing=1.2,
        )

        # Ajustar para que la leyenda no se corte
        self.figure.subplots_adjust(left=0.05, right=0.65, top=0.92, bottom=0.05)

        self.canvas.draw()

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
