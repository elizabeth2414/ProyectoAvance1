"""Ventana principal del sistema en PyQt6."""

import os
import shutil
import sqlite3
from datetime import datetime

from PyQt6.QtCore import QTimer, QSize, Qt
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from .componentes.sidebar import Sidebar
from .estilos.qss import get_global_stylesheet
from .vista_clientes import VistaClientes
from .vista_dashboard import VistaDashboard
from .vista_productos import VistaProductos
from .vista_proveedores import VistaProveedores
from .vista_reportes import VistaReportes
from .vista_ventas import VistaVentas


class _VistaPlaceholder(QWidget):
    """Vista temporal para modulos no migrados aun."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        t = QLabel(titulo)
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(t)

        desc = QLabel("Vista pendiente de migracion a PyQt6.\nLa logica del modulo se mantiene intacta.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addStretch(1)


class AppPrincipal(QMainWindow):
    """Ventana principal con sidebar y contenido apilado."""

    def __init__(self, conexion: sqlite3.Connection, usuario, on_logout=None):
        super().__init__()
        self.conexion = conexion
        self.usuario = usuario
        self.on_logout_callback = on_logout
        self._vistas = {
            "dashboard": VistaDashboard,
            "clientes": VistaClientes,
            "productos": VistaProductos,
            "proveedores": VistaProveedores,
            "ventas": VistaVentas,
            "reportes": VistaReportes,
        }
        self._cerrando_por_logout = False

        self.setWindowTitle(f"Sistema de Ventas - {self.usuario.username}")
        self.resize(1250, 760)
        self.setMinimumSize(1040, 650)
        self.setStyleSheet(get_global_stylesheet())
        self._centrar_ventana()

        self._crear_layout()
        self._crear_barra_estado()
        self._configurar_timers()
        self.navegar("dashboard")
        self.sidebar.seleccionar("dashboard")

    def _centrar_ventana(self):
        screen = self.screen() or QApplication.primaryScreen()
        if not screen:
            return
        geom = screen.availableGeometry()
        x = (geom.width() - self.width()) // 2 + geom.x()
        y = (geom.height() - self.height()) // 2 + geom.y()
        self.move(x, y)

    def _crear_layout(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(central, self.usuario)
        self.sidebar.navegacion_cambiada.connect(self.navegar)
        self.sidebar.logout_solicitado.connect(self._cerrar_sesion)
        self.sidebar.backup_solicitado.connect(self._crear_backup)

        self.stack = QStackedWidget(central)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

    def _crear_barra_estado(self):
        barra = QStatusBar(self)
        self.setStatusBar(barra)

        clientes_widget, self.lbl_clientes = self._crear_label_con_icono("mdi6.account-group", "Clientes: 0", barra)
        productos_widget, self.lbl_productos = self._crear_label_con_icono("mdi6.package-variant", "Productos: 0", barra)
        ventas_widget, self.lbl_ventas = self._crear_label_con_icono("mdi6.cart", "Ventas: 0", barra)
        usuario_widget, self.lbl_usuario = self._crear_label_con_icono(
            "mdi6.account-circle",
            f"Usuario: {self.usuario.username} ({self.usuario.rol})",
            barra,
        )
        hora_widget, self.lbl_hora = self._crear_label_con_icono("mdi6.clock-outline", "", barra)

        barra.addWidget(clientes_widget)
        barra.addWidget(productos_widget)
        barra.addWidget(ventas_widget)
        barra.addPermanentWidget(usuario_widget)
        barra.addPermanentWidget(hora_widget)

        self._actualizar_conteos()
        self._actualizar_hora()

    def _crear_label_con_icono(self, icono_nombre: str, texto: str, parent):
        widget = QWidget(parent)
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        icono_lbl = QLabel()
        pixmap = qta.icon(icono_nombre, color="#B0B0B0").pixmap(QSize(14, 14))
        icono_lbl.setPixmap(pixmap)

        txt_lbl = QLabel(texto)
        txt_lbl.setStyleSheet("color: #B0B0B0;")

        lay.addWidget(icono_lbl)
        lay.addWidget(txt_lbl)
        return widget, txt_lbl

    def _configurar_timers(self):
        self.timer_conteos = QTimer(self)
        self.timer_conteos.timeout.connect(self._actualizar_conteos)
        self.timer_conteos.start(30000)

        self.timer_hora = QTimer(self)
        self.timer_hora.timeout.connect(self._actualizar_hora)
        self.timer_hora.start(1000)

    def navegar(self, modulo: str):
        if modulo not in self._vistas:
            return

        widget_actual = self.stack.currentWidget()
        if widget_actual:
            self.stack.removeWidget(widget_actual)
            widget_actual.deleteLater()

        nueva_vista = self._vistas[modulo](self.stack, self.conexion, self.usuario)
        self.stack.addWidget(nueva_vista)
        self.stack.setCurrentWidget(nueva_vista)

        if hasattr(nueva_vista, "actualizar"):
            nueva_vista.actualizar()
        self._actualizar_conteos()

    def _actualizar_conteos(self):
        from controladores.cliente_controller import ClienteController
        from controladores.producto_controller import ProductoController
        from controladores.venta_controller import VentaController

        try:
            clientes = ClienteController(self.conexion).contar()
            productos = ProductoController(self.conexion).contar()
            ventas = VentaController(self.conexion).contar()
            self.lbl_clientes.setText(f"Clientes: {clientes}")
            self.lbl_productos.setText(f"Productos: {productos}")
            self.lbl_ventas.setText(f"Ventas: {ventas}")
        except Exception:
            self.lbl_clientes.setText("Clientes: -")
            self.lbl_productos.setText("Productos: -")
            self.lbl_ventas.setText("Ventas: -")

    def _actualizar_hora(self):
        self.lbl_hora.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def _crear_backup(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para backup")
        if not carpeta:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_backup = f"backup_{timestamp}.db"
            ruta_backup = os.path.join(carpeta, nombre_backup)

            cursor = self.conexion.cursor()
            cursor.execute("PRAGMA database_list")
            db_info = cursor.fetchone()
            ruta_bd = db_info[2] if db_info else "sistema_ventas.db"
            shutil.copy2(ruta_bd, ruta_backup)

            QMessageBox.information(self, "Backup Exitoso", f"Copia de seguridad creada:\n{ruta_backup}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Error al crear backup:\n{exc}")

    def _cerrar_sesion(self):
        respuesta = QMessageBox.question(
            self,
            "Cerrar Sesion",
            "Desea cerrar la sesion?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self._cerrando_por_logout = True
            self.close()
            if self.on_logout_callback:
                self.on_logout_callback()

    def closeEvent(self, event: QCloseEvent):
        if self._cerrando_por_logout:
            event.accept()
            return
        respuesta = QMessageBox.question(
            self,
            "Salir",
            "Desea salir del sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
