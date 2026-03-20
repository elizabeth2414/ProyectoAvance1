"""Vista de ventas en PyQt6 con flujo completo de operaciones."""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

raiz_proyecto = Path(__file__).resolve().parents[1]
if str(raiz_proyecto) not in sys.path:
    sys.path.insert(0, str(raiz_proyecto))

from controladores.cliente_controller import ClienteController
from controladores.producto_controller import ProductoController
from controladores.venta_controller import VentaController
from modelos.venta import Venta
from vistas.componentes.tabla import TablaEstilizada
from vistas.estilos.colores import (
    PRIMARY,
    DANGER,
    SUCCESS,
    WARNING,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from vistas.estilos.qss import get_global_stylesheet
from vistas.vista_factura import generar_factura_pdf


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


ICONOS_DIALOGO = {
    "Nueva Venta": ("mdi6.cart-plus", PRIMARY),
}


def _campo_con_icono(icono_nombre, widget, color="#B0B0B0"):
    frame = QFrame()
    frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 8px; }")
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(8, 4, 8, 4)
    lay.setSpacing(8)
    icono_lbl = QLabel()
    icono_lbl.setPixmap(qta.icon(icono_nombre, color=color).pixmap(QSize(16, 16)))
    icono_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    lay.addWidget(icono_lbl)
    lay.addWidget(widget, 1)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return frame


def _aplicar_estilo_boton(btn: QPushButton, clase: str):
    btn.setProperty("class", clase)
    btn.style().unpolish(btn)
    btn.style().polish(btn)


def _msg(parent, icon: QMessageBox.Icon, title: str, text: str, buttons=QMessageBox.StandardButton.Ok):
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    msg.setStyleSheet(f"background-color: {SURFACE}; color: {TEXT_PRIMARY};")
    return msg.exec()


def _centrar_dialogo(dialog: QDialog):
    """Centra un diálogo en el centro de la pantalla."""
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen:
        geom = screen.availableGeometry()
        dialog_geom = dialog.geometry()
        x = (geom.width() - dialog_geom.width()) // 2 + geom.x()
        y = (geom.height() - dialog_geom.height()) // 2 + geom.y()
        dialog.move(x, y)


class _DialogNuevaVenta(QDialog):
    def __init__(self, parent, clientes: list[str], productos: list[dict], proximo_id: str = ""):
        super().__init__(parent)
        titulo = "Nueva Venta"
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(560, 330)
        self.setMinimumWidth(520)
        self.setStyleSheet(get_global_stylesheet())
        _centrar_dialogo(self)
        self.productos = productos

        layout = QVBoxLayout(self)
        icono_nombre, icono_color = ICONOS_DIALOGO.get(titulo, ("mdi6.pencil", PRIMARY))
        fila_titulo = QHBoxLayout()
        lbl_icono = QLabel()
        lbl_icono.setPixmap(qta.icon(icono_nombre, color=icono_color).pixmap(QSize(28, 28)))
        titulo_dlg = QLabel(titulo)
        titulo_dlg.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo_dlg.setStyleSheet(f"color: {PRIMARY};")
        fila_titulo.addWidget(lbl_icono)
        fila_titulo.addWidget(titulo_dlg)
        fila_titulo.addStretch(1)
        layout.addLayout(fila_titulo)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {PRIMARY}; margin-bottom: 8px;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(16)
        form.setContentsMargins(8, 8, 8, 8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        id_texto = proximo_id if proximo_id else "Se generará automáticamente"
        self.lbl_id_preview = QLabel(id_texto)
        self.lbl_id_preview.setStyleSheet(f"color: #00E676; font-style: italic;")
        self.lbl_id_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form.addRow("ID Venta:", _campo_con_icono("mdi6.identifier", self.lbl_id_preview, "#00E676"))

        self.combo_cliente = QComboBox(self)
        self.combo_cliente.addItems(clientes)
        self.combo_cliente.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.combo_producto = QComboBox(self)
        self.combo_producto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for p in productos:
            self.combo_producto.addItem(f"{p['id']} - {p['nombre']} (Stock: {p['stock']})", p)

        self.lbl_stock = QLabel("Stock disponible: -")
        self.lbl_stock.setStyleSheet(f"color: {TEXT_SECONDARY};")

        self.input_cantidad = QDoubleSpinBox(self)
        self.input_cantidad.setMinimum(0.01)
        self.input_cantidad.setMaximum(999999.99)
        self.input_cantidad.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input_cantidad.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_cantidad.setValue(1.0)

        slider_layout = QHBoxLayout()
        self.slider_desc = QSlider(Qt.Orientation.Horizontal)
        self.slider_desc.setRange(0, 50)
        self.lbl_desc = QLabel("0%")
        self.slider_desc.valueChanged.connect(lambda v: self.lbl_desc.setText(f"{v}%"))
        slider_layout.addWidget(self.slider_desc)
        slider_layout.addWidget(self.lbl_desc)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {DANGER};")

        slider_widget = QWidget()
        slider_widget.setLayout(slider_layout)

        form.addRow("Cliente:", _campo_con_icono("mdi6.account", self.combo_cliente))
        form.addRow("Producto:", _campo_con_icono("mdi6.package-variant", self.combo_producto))
        form.addRow("", self.lbl_stock)
        form.addRow("Cantidad:", _campo_con_icono("mdi6.numeric", self.input_cantidad))
        form.addRow("Descuento:", _campo_con_icono("mdi6.sale", slider_widget))
        layout.addLayout(form)
        layout.addWidget(self.lbl_error)

        btns = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        _aplicar_estilo_boton(btn_cancelar, "btn-neutral")
        btn_cancelar.setIcon(qta.icon("mdi6.close", color="white"))
        btn_cancelar.setIconSize(QSize(16, 16))
        btn_cancelar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_cancelar.setMinimumHeight(44)
        btn_ok = QPushButton("Realizar Venta")
        _aplicar_estilo_boton(btn_ok, "btn-success")
        btn_ok.setIcon(qta.icon("mdi6.content-save", color="white"))
        btn_ok.setIconSize(QSize(16, 16))
        btn_ok.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_ok.setMinimumHeight(44)
        btn_cancelar.clicked.connect(self.reject)
        btn_ok.clicked.connect(self._validar)
        btns.addWidget(btn_cancelar)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

        self.combo_producto.currentIndexChanged.connect(self._actualizar_stock)
        self._actualizar_stock()

    def _actualizar_stock(self):
        data = self.combo_producto.currentData()
        stock = int(data["stock"]) if data else 0
        self.lbl_stock.setText(f"Stock disponible: {stock}")

    def _validar(self):
        data = self.combo_producto.currentData()
        if not data:
            self.lbl_error.setText("Seleccione un producto válido")
            return
        if self.input_cantidad.value() > float(data["stock"]):
            self.lbl_error.setText("La cantidad supera el stock disponible")
            return
        self.accept()

    def datos(self) -> dict:
        cliente_texto = self.combo_cliente.currentText()
        producto_data = self.combo_producto.currentData() or {}
        return {
            "cliente_id": cliente_texto.split(" - ")[0],
            "producto_id": producto_data.get("id", ""),
            "cantidad": float(self.input_cantidad.value()),
            "descuento": float(self.slider_desc.value()),
        }


class VistaVentas(QWidget):
    """Gestión de ventas con filtros, devoluciones y facturación."""

    def __init__(self, parent, conexion: sqlite3.Connection, usuario):
        super().__init__(parent)
        self.conexion = conexion
        self.usuario = usuario
        self.venta_ctrl = VentaController(conexion)
        self.cliente_ctrl = ClienteController(conexion)
        self.producto_ctrl = ProductoController(conexion)
        self.venta_id_seleccionada = ""

        self._crear_ui()
        self.actualizar()

    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(_crear_titulo("mdi6.cart", "Gestión de Ventas", PRIMARY))

        self.input_buscar = QLineEdit(self)
        self.input_buscar.setPlaceholderText("Buscar por ID de venta")
        self.input_buscar.setMinimumWidth(200)
        self.input_buscar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_buscar.textChanged.connect(self._aplicar_filtros)
        top.addWidget(self.input_buscar, 1)

        self.combo_estado = QComboBox(self)
        self.combo_estado.addItems(["Todas", "Activas", "Devueltas"])
        self.combo_estado.currentTextChanged.connect(self._aplicar_filtros)
        top.addWidget(self.combo_estado)
        layout.addLayout(top)

        barra = QHBoxLayout()
        btn_nueva = QPushButton(" Nueva Venta")
        _aplicar_estilo_boton(btn_nueva, "btn-success")
        btn_nueva.setIcon(qta.icon("mdi6.cart-plus", color="#FFFFFF"))
        btn_nueva.setIconSize(QSize(16, 16))
        btn_nueva.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_nueva.setMinimumHeight(48)
        btn_nueva.clicked.connect(self._nueva_venta)

        btn_devolver = QPushButton(" Devolver")
        _aplicar_estilo_boton(btn_devolver, "btn-warning")
        btn_devolver.setIcon(qta.icon("mdi6.arrow-u-left-top", color="#1A1A1A"))
        btn_devolver.setIconSize(QSize(16, 16))
        btn_devolver.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_devolver.setMinimumHeight(48)
        btn_devolver.clicked.connect(self._devolver)

        btn_factura = QPushButton(" Factura PDF")
        _aplicar_estilo_boton(btn_factura, "btn-purple")
        btn_factura.setIcon(qta.icon("mdi6.file-pdf-box", color="#FFFFFF"))
        btn_factura.setIconSize(QSize(16, 16))
        btn_factura.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_factura.setMinimumHeight(48)
        btn_factura.clicked.connect(self._generar_factura)

        btn_eliminar = QPushButton(" Eliminar")
        _aplicar_estilo_boton(btn_eliminar, "btn-danger")
        btn_eliminar.setIcon(qta.icon("fa6s.trash", color="#FFFFFF"))
        btn_eliminar.setIconSize(QSize(16, 16))
        btn_eliminar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_eliminar.setMinimumHeight(48)
        btn_eliminar.setEnabled(self.usuario.es_admin())
        btn_eliminar.clicked.connect(self._eliminar)

        btn_actualizar = QPushButton(" Actualizar")
        _aplicar_estilo_boton(btn_actualizar, "btn-neutral")
        btn_actualizar.setIcon(qta.icon("mdi6.refresh", color="#FFFFFF"))
        btn_actualizar.setIconSize(QSize(16, 16))
        btn_actualizar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_actualizar.setMinimumHeight(48)
        btn_actualizar.clicked.connect(self.actualizar)

        barra.addWidget(btn_nueva)
        barra.addWidget(btn_devolver)
        barra.addWidget(btn_factura)
        barra.addWidget(btn_eliminar)
        barra.addWidget(btn_actualizar)
        layout.addLayout(barra)

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("color: #3D3D3D; margin: 4px 0px;")
        layout.addWidget(separador)

        resumen = QFrame(self)
        resumen.setMinimumHeight(50)
        resumen.setStyleSheet(
            """
            QFrame {
                background-color: #1A1A2E;
                border-radius: 10px;
                border: 1px solid #1565C0;
                padding: 8px;
            }
            """
        )
        resumen_layout = QHBoxLayout(resumen)
        self.lbl_total_activas = QLabel("Total Ventas Activas: 0")
        self.lbl_total_activas.setStyleSheet("color: #B0B0B0; font-size: 14px;")
        self.lbl_monto_total = QLabel("Monto Total: S/ 0.00")
        self.lbl_monto_total.setStyleSheet("color: #00E676; font-weight: 700; font-size: 16px;")
        resumen_layout.addWidget(self.lbl_total_activas)
        resumen_layout.addStretch(1)
        resumen_layout.addWidget(self.lbl_monto_total)
        layout.addWidget(resumen)

        self.tabla = TablaEstilizada(self)
        self.tabla.fila_seleccionada.connect(self._set_venta_id)
        self.tabla.cellDoubleClicked.connect(lambda *_: self._mostrar_detalle())
        layout.addWidget(self.tabla, 1)

    def _set_venta_id(self, venta_id: str):
        self.venta_id_seleccionada = venta_id

    def _ventas_filtradas(self):
        ventas = self.venta_ctrl.listar()
        estado = self.combo_estado.currentText()
        texto = self.input_buscar.text().strip().lower()

        if estado == "Activas":
            ventas = [v for v in ventas if not v.es_devuelta()]
        elif estado == "Devueltas":
            ventas = [v for v in ventas if v.es_devuelta()]

        if texto:
            ventas = [v for v in ventas if texto in (v.id or "").lower()]
        return ventas

    def _cargar_tabla(self, ventas):
        datos = []
        total_activo = 0.0
        total_count = 0

        for v in ventas:
            try:
                cliente = self.cliente_ctrl.buscar(v.cliente_id)
                cliente_nombre = cliente.nombre
            except Exception:
                cliente_nombre = v.cliente_id
            try:
                producto = self.producto_ctrl.buscar(v.producto_id)
                producto_nombre = producto.nombre
                total = v.calcular_total_con_precio(float(producto.precio))
                precio = float(producto.precio)
            except Exception:
                producto_nombre = v.producto_id
                total = 0.0
                precio = 0.0

            if not v.es_devuelta():
                total_activo += total
                total_count += 1

            datos.append(
                {
                    "ID": v.id,
                    "CLIENTE": cliente_nombre,
                    "PRODUCTO": producto_nombre,
                    "CANT.": f"{float(v.cantidad):.2f}",
                    "DESC.%": f"{float(v.descuento):.0f}",
                    "TOTAL": f"S/ {total:.2f}",
                    "FECHA": (v.fecha or "")[:16],
                    "ESTADO": "DEVUELTA" if v.es_devuelta() else "ACTIVA",
                    "__precio": precio,
                }
            )

        def _tag(row: dict) -> str:
            return "devuelta" if row["ESTADO"] == "DEVUELTA" else ""

        tabla_datos = [{k: val for k, val in d.items() if not k.startswith("__")} for d in datos]
        self._cache_detalle = {d["ID"]: d for d in datos}
        self.tabla.cargar_datos(tabla_datos, _tag)
        self.lbl_total_activas.setText(f"Total Ventas Activas: {total_count}")
        self.lbl_monto_total.setText(f"Monto Total: S/ {total_activo:.2f}")

    def _aplicar_filtros(self):
        try:
            self._cargar_tabla(self._ventas_filtradas())
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _nueva_venta(self):
        try:
            clientes = [f"{c.id} - {c.nombre}" for c in self.cliente_ctrl.listar()]
            productos = [
                {"id": p.id, "nombre": p.nombre, "stock": float(p.stock)}
                for p in self.producto_ctrl.listar()
                if float(p.stock) > 0
            ]
            if not clientes or not productos:
                _msg(self, QMessageBox.Icon.Warning, "Atención", "No hay clientes o productos con stock disponibles")
                return

            proximo_id = self.venta_ctrl.previsualizar_id()
            dlg = _DialogNuevaVenta(self, clientes, productos, proximo_id)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            data = dlg.datos()
            venta = Venta(
                id=None,
                cliente=data["cliente_id"],
                producto=data["producto_id"],
                cantidad=data["cantidad"],
                descuento=data["descuento"],
                fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                estado="activa",
            )
            self.venta_ctrl.agregar(venta, reducir_stock=True)
            producto = self.producto_ctrl.buscar(data["producto_id"])
            total = venta.calcular_total_con_precio(float(producto.precio))
            _msg(self, QMessageBox.Icon.Information, "Éxito", f"Venta registrada: {venta.id}\nTotal: S/ {total:.2f}")
            self.actualizar()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _mostrar_detalle(self):
        if not self.venta_id_seleccionada:
            return
        try:
            venta = self.venta_ctrl.buscar(self.venta_id_seleccionada)
            cliente = self.cliente_ctrl.buscar(venta.cliente_id)
            producto = self.producto_ctrl.buscar(venta.producto_id)
            total = venta.calcular_total_con_precio(float(producto.precio))

            dlg = QDialog(self)
            dlg.setWindowTitle("Detalle de Venta")
            dlg.setModal(True)
            dlg.resize(460, 340)
            lay = QVBoxLayout(dlg)
            form = QFormLayout()
            form.addRow("ID:", QLabel(venta.id))
            form.addRow("Cliente:", QLabel(cliente.nombre))
            form.addRow("Producto:", QLabel(producto.nombre))
            form.addRow("Cantidad:", QLabel(f"{float(venta.cantidad):.2f}"))
            form.addRow("Precio unitario:", QLabel(f"S/ {float(producto.precio):.2f}"))
            form.addRow("Descuento:", QLabel(f"{float(venta.descuento):.0f}%"))
            form.addRow("Total:", QLabel(f"S/ {total:.2f}"))
            form.addRow("Fecha:", QLabel(venta.fecha or ""))
            form.addRow("Estado:", QLabel(venta.estado.upper()))
            lay.addLayout(form)
            btn = QPushButton("Cerrar")
            _aplicar_estilo_boton(btn, "btn-neutral")
            btn.clicked.connect(dlg.accept)
            lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
            dlg.exec()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _devolver(self):
        if not self.venta_id_seleccionada:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Seleccione una venta")
            return
        try:
            venta = self.venta_ctrl.buscar(self.venta_id_seleccionada)
            if venta.es_devuelta():
                _msg(self, QMessageBox.Icon.Warning, "Atención", "La venta ya está devuelta")
                return
            r = _msg(
                self,
                QMessageBox.Icon.Question,
                "Confirmar",
                f"¿Desea devolver la venta {self.venta_id_seleccionada}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if r != int(QMessageBox.StandardButton.Yes):
                return
            self.venta_ctrl.devolver(self.venta_id_seleccionada)
            _msg(self, QMessageBox.Icon.Information, "Éxito", "Venta devuelta correctamente")
            self.actualizar()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _eliminar(self):
        if not self.venta_id_seleccionada:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Seleccione una venta")
            return
        r = _msg(
            self,
            QMessageBox.Icon.Question,
            "Confirmar",
            f"¿Desea eliminar la venta {self.venta_id_seleccionada}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != int(QMessageBox.StandardButton.Yes):
            return
        try:
            self.venta_ctrl.eliminar(self.venta_id_seleccionada)
            _msg(self, QMessageBox.Icon.Information, "Éxito", "Venta eliminada correctamente")
            self.actualizar()
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def _generar_factura(self):
        if not self.venta_id_seleccionada:
            _msg(self, QMessageBox.Icon.Warning, "Atención", "Seleccione una venta")
            return
        try:
            generar_factura_pdf(self.conexion, self.venta_id_seleccionada)
        except Exception as exc:
            _msg(self, QMessageBox.Icon.Critical, "Error", str(exc))

    def actualizar(self):
        self.venta_id_seleccionada = ""
        self._aplicar_filtros()
