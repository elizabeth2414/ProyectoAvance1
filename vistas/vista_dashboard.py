"""Vista dashboard en PyQt6 con resumen y tablas de estado."""

import sqlite3

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QSizePolicy, QVBoxLayout, QWidget
import qtawesome as qta

from controladores.cliente_controller import ClienteController
from controladores.producto_controller import ProductoController
from controladores.venta_controller import VentaController
from vistas.componentes.tabla import TablaEstilizada
from vistas.componentes.tarjeta import TarjetaResumen
from vistas.estilos.colores import *


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


class VistaDashboard(QWidget):
    """Dashboard principal con tarjetas y tablas de monitoreo."""

    def __init__(self, parent, conexion: sqlite3.Connection, usuario):
        super().__init__(parent)
        self.conexion = conexion
        self.usuario = usuario

        self.cliente_ctrl = ClienteController(conexion)
        self.producto_ctrl = ProductoController(conexion)
        self.venta_ctrl = VentaController(conexion)

        self._crear_ui()
        self.actualizar()

    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(_crear_titulo("mdi6.view-dashboard", "Dashboard", PRIMARY))

        grid_tarjetas = QGridLayout()
        grid_tarjetas.setSpacing(12)
        grid_tarjetas.setColumnStretch(0, 1)
        grid_tarjetas.setColumnStretch(1, 1)
        grid_tarjetas.setColumnStretch(2, 1)
        grid_tarjetas.setColumnStretch(3, 1)

        self.card_clientes = TarjetaResumen(self, "Total Clientes", "0", SUCCESS, icono_nombre="mdi6.account-group")
        self.card_productos = TarjetaResumen(self, "Total Productos", "0", PRIMARY, icono_nombre="mdi6.package-variant")
        self.card_ventas = TarjetaResumen(self, "Total Ventas", "0", "#7B1FA2", icono_nombre="mdi6.cart")
        self.card_monto = TarjetaResumen(self, "Monto Total", "S/ 0.00", WARNING, icono_nombre="mdi6.cash-multiple")

        grid_tarjetas.addWidget(self.card_clientes, 0, 0)
        grid_tarjetas.addWidget(self.card_productos, 0, 1)
        grid_tarjetas.addWidget(self.card_ventas, 0, 2)
        grid_tarjetas.addWidget(self.card_monto, 0, 3)
        layout.addLayout(grid_tarjetas)

        fila_tablas = QHBoxLayout()
        fila_tablas.setSpacing(12)

        panel_stock = self._crear_panel_tabla("⚠ Productos con Stock Crítico", DANGER)
        self.tabla_stock = TablaEstilizada(self)
        panel_stock.layout().addWidget(self.tabla_stock, 1)
        fila_tablas.addWidget(panel_stock, 1)

        panel_ventas = self._crear_panel_tabla("🕐 Últimas 5 Ventas", TEXT_PRIMARY)
        self.tabla_ventas = TablaEstilizada(self)
        panel_ventas.layout().addWidget(self.tabla_ventas, 1)
        fila_tablas.addWidget(panel_ventas, 1)

        layout.addLayout(fila_tablas, 1)

    def _crear_panel_tabla(self, titulo: str, color_titulo: str) -> QFrame:
        frame = QFrame(self)
        frame.setProperty("class", "card")
        panel_layout = QVBoxLayout(frame)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(8)

        lbl = QLabel(titulo)
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {color_titulo};")
        panel_layout.addWidget(lbl)
        return frame

    def actualizar_tarjetas(self):
        """Actualiza los contadores superiores del dashboard."""
        total_clientes = self.cliente_ctrl.contar()
        total_productos = self.producto_ctrl.contar()
        resumen = self.venta_ctrl.obtener_resumen_ventas()

        self.card_clientes.actualizar_valor(str(total_clientes))
        self.card_productos.actualizar_valor(str(total_productos))
        self.card_ventas.actualizar_valor(str(resumen["total_ventas"]))
        self.card_monto.actualizar_valor(f"S/ {resumen['monto_total']:.2f}")

    def _actualizar_tabla_stock(self):
        productos = self.producto_ctrl.listar_stock_critico()
        datos = [
            {
                "ID": p.id,
                "PRODUCTO": p.nombre,
                "STOCK": int(p.stock),
                "MÍNIMO": int(p.stock_minimo),
                "ESTADO": "SIN STOCK" if int(p.stock) == 0 else "STOCK CRITICO",
            }
            for p in productos
        ]

        def _tag(registro: dict) -> str:
            if int(registro["STOCK"]) == 0:
                return "critico"
            if int(registro["STOCK"]) < int(registro["MÍNIMO"]):
                return "advertencia"
            return ""

        self.tabla_stock.cargar_datos(datos, _tag)

    def _actualizar_tabla_ventas(self):
        cursor = self.venta_ctrl.conn.cursor()
        cursor.execute(
            """
            SELECT
                v.id AS ID,
                c.nombre AS CLIENTE,
                p.nombre AS PRODUCTO,
                (p.precio * v.cantidad * (1 - (v.descuento / 100.0))) AS TOTAL,
                substr(v.fecha, 1, 10) AS FECHA
            FROM ventas v
            JOIN clientes c ON c.id = v.cliente_id
            JOIN productos p ON p.id = v.producto_id
            ORDER BY v.fecha DESC
            LIMIT 5
            """
        )
        rows = cursor.fetchall()
        datos = []
        for row in rows:
            datos.append(
                {
                    "ID": row["ID"],
                    "CLIENTE": row["CLIENTE"],
                    "PRODUCTO": row["PRODUCTO"],
                    "TOTAL": f"S/ {float(row['TOTAL'] or 0):.2f}",
                    "FECHA": row["FECHA"],
                }
            )
        self.tabla_ventas.cargar_datos(datos)

    def actualizar(self):
        """Refresca tarjetas y tablas del dashboard."""
        try:
            self.actualizar_tarjetas()
            self._actualizar_tabla_stock()
            self._actualizar_tabla_ventas()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
