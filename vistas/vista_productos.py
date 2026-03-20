"""Vista de productos en PyQt6 con filtros y CRUD."""

import sqlite3

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from controladores.producto_controller import ProductoController
from controladores.proveedor_controller import ProveedorController
from modelos.producto import Producto
from vistas.componentes.tabla import TablaEstilizada
from vistas.estilos.colores import *
from vistas.estilos.qss import get_global_stylesheet


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
    "Agregar Producto": ("mdi6.package-variant-plus", PRIMARY),
    "Editar Producto": ("mdi6.package-variant", PRIMARY),
}


def _campo_con_icono(icono_nombre, widget, color="#B0B0B0"):
    frame = QFrame()
    frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 8px; }")
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(8, 4, 8, 4)
    lay.setSpacing(8)
    icono_lbl = QLabel()
    icono_lbl.setPixmap(qta.icon(icono_nombre, color=color).pixmap(QSize(16, 16)))
    lay.addWidget(icono_lbl)
    lay.addWidget(widget)
    return frame


def _centrar_dialogo(dialog: QDialog):
    """Centra un diálogo en el centro de la pantalla."""
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen:
        geom = screen.availableGeometry()
        dialog_geom = dialog.geometry()
        x = (geom.width() - dialog_geom.width()) // 2 + geom.x()
        y = (geom.height() - dialog_geom.height()) // 2 + geom.y()
        dialog.move(x, y)


class _ProductoDialog(QDialog):
    def __init__(self, parent, titulo: str, categorias: list[str], proveedores: list[str], datos: dict | None = None, proximo_id: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(560, 420)
        self.setMinimumWidth(520)
        self.setStyleSheet(get_global_stylesheet())
        _centrar_dialogo(self)
        data = datos or {}

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
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        id_texto = data.get("id", "") if data else proximo_id
        self.input_id = QLineEdit(id_texto)
        self.input_id.setReadOnly(True)
        self.input_id.setStyleSheet("color: #00E676; font-style: italic;")

        self.input_nombre = QLineEdit(data.get("nombre", ""))
        self.input_nombre.setPlaceholderText("Ej.: Laptop Lenovo ThinkPad")

        self.input_precio = QDoubleSpinBox()
        self.input_precio.setDecimals(2)
        self.input_precio.setMaximum(9999999.99)
        self.input_precio.setPrefix("S/ ")
        self.input_precio.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input_precio.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_precio.setValue(float(data.get("precio", 0) or 0))

        self.combo_categoria = QComboBox()
        self.combo_categoria.setEditable(True)
        self.combo_categoria.addItems([c for c in categorias if c])
        self.combo_categoria.setCurrentText(data.get("categoria", ""))
        self.combo_categoria.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if self.combo_categoria.lineEdit():
            self.combo_categoria.lineEdit().setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.combo_categoria.lineEdit().setPlaceholderText("Ej.: Accesorios")

        self.input_stock = QSpinBox()
        self.input_stock.setMinimum(0)
        self.input_stock.setMaximum(10_000_000)
        self.input_stock.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input_stock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_stock.setValue(int(data.get("stock", 0) or 0))

        self.input_stock_minimo = QSpinBox()
        self.input_stock_minimo.setMinimum(0)
        self.input_stock_minimo.setMaximum(10_000_000)
        self.input_stock_minimo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input_stock_minimo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_stock_minimo.setValue(int(data.get("stock_minimo", 5) or 5))

        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItem("")
        self.combo_proveedor.addItems(proveedores)
        self.combo_proveedor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        prov_id = data.get("proveedor_id", "")
        if prov_id:
            for i in range(self.combo_proveedor.count()):
                if self.combo_proveedor.itemText(i).startswith(f"{prov_id} - "):
                    self.combo_proveedor.setCurrentIndex(i)
                    break

        self.input_descripcion = QLineEdit(data.get("descripcion", ""))
        self.input_descripcion.setPlaceholderText("Ej.: Equipo de alto rendimiento")

        form.addRow("ID:", _campo_con_icono("mdi6.identifier", self.input_id))
        form.addRow("Nombre *:", _campo_con_icono("mdi6.tag", self.input_nombre))
        form.addRow("Precio *:", _campo_con_icono("mdi6.cash", self.input_precio))
        form.addRow("Categoría:", _campo_con_icono("mdi6.shape", self.combo_categoria))
        form.addRow("Stock *:", _campo_con_icono("mdi6.package-variant", self.input_stock))
        form.addRow("Stock Mínimo:", _campo_con_icono("mdi6.package-variant", self.input_stock_minimo))
        form.addRow("Proveedor:", _campo_con_icono("fa6s.truck", self.combo_proveedor))
        form.addRow("Descripción:", _campo_con_icono("mdi6.text", self.input_descripcion))
        layout.addLayout(form)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {DANGER};")
        layout.addWidget(self.lbl_error)

        fila_btn = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setProperty("class", "btn-neutral")
        btn_cancelar.setIcon(qta.icon("mdi6.close", color="white"))
        btn_cancelar.setIconSize(QSize(16, 16))
        btn_cancelar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_cancelar.setMinimumHeight(44)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setProperty("class", "btn-success")
        btn_guardar.setIcon(qta.icon("mdi6.content-save", color="white"))
        btn_guardar.setIconSize(QSize(16, 16))
        btn_guardar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_guardar.setMinimumHeight(44)
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar.clicked.connect(self._validar)
        fila_btn.addWidget(btn_cancelar)
        fila_btn.addWidget(btn_guardar)
        layout.addLayout(fila_btn)

    def showEvent(self, event):
        super().showEvent(event)
        _centrar_dialogo(self)

    def _validar(self):
        if not self.input_nombre.text().strip():
            self.lbl_error.setText("El nombre es obligatorio")
            return
        if self.input_precio.value() <= 0:
            self.lbl_error.setText("El precio debe ser mayor a 0")
            return
        self.accept()

    def datos(self) -> dict:
        proveedor_texto = self.combo_proveedor.currentText().strip()
        proveedor_id = proveedor_texto.split(" - ")[0] if " - " in proveedor_texto else ""
        return {
            "id": self.input_id.text().strip(),
            "nombre": self.input_nombre.text().strip(),
            "precio": float(self.input_precio.value()),
            "categoria": self.combo_categoria.currentText().strip(),
            "stock": int(self.input_stock.value()),
            "stock_minimo": int(self.input_stock_minimo.value()),
            "proveedor_id": proveedor_id,
            "descripcion": self.input_descripcion.text().strip(),
        }


class VistaProductos(QWidget):
    """Gestión de productos con filtro por categoría y CRUD."""

    def __init__(self, parent, conexion: sqlite3.Connection, usuario):
        super().__init__(parent)
        self.conexion = conexion
        self.usuario = usuario
        self.controller = ProductoController(conexion)
        self.proveedor_controller = ProveedorController(conexion)
        self.id_seleccionado = ""

        self._crear_ui()
        self.actualizar()

    def _crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(_crear_titulo("mdi6.package-variant", "Gestión de Productos", PRIMARY))

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por nombre...")
        self.input_buscar.setMinimumWidth(200)
        self.input_buscar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_buscar.textChanged.connect(self._aplicar_filtros)
        top.addWidget(self.input_buscar, 1)

        self.combo_categoria = QComboBox()
        self.combo_categoria.setMinimumWidth(190)
        self.combo_categoria.currentTextChanged.connect(self._aplicar_filtros)
        top.addWidget(self.combo_categoria)
        layout.addLayout(top)

        barra = QHBoxLayout()
        self.btn_agregar = QPushButton(" Agregar")
        self.btn_agregar.setProperty("class", "btn-success")
        self.btn_agregar.setIcon(qta.icon("fa6s.plus", color="#FFFFFF"))
        self.btn_agregar.setIconSize(QSize(16, 16))
        self.btn_agregar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_agregar.setMinimumHeight(48)
        self.btn_agregar.clicked.connect(self._agregar)
        barra.addWidget(self.btn_agregar)

        self.btn_editar = QPushButton(" Editar")
        self.btn_editar.setProperty("class", "btn-primary")
        self.btn_editar.setIcon(qta.icon("fa6s.pen-to-square", color="#FFFFFF"))
        self.btn_editar.setIconSize(QSize(16, 16))
        self.btn_editar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_editar.setMinimumHeight(48)
        self.btn_editar.clicked.connect(self._editar)
        barra.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton(" Eliminar")
        self.btn_eliminar.setProperty("class", "btn-danger")
        self.btn_eliminar.setIcon(qta.icon("fa6s.trash", color="#FFFFFF"))
        self.btn_eliminar.setIconSize(QSize(16, 16))
        self.btn_eliminar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_eliminar.setMinimumHeight(48)
        self.btn_eliminar.setEnabled(self.usuario.es_admin())
        self.btn_eliminar.clicked.connect(self._eliminar)
        barra.addWidget(self.btn_eliminar)

        self.btn_actualizar = QPushButton(" Actualizar")
        self.btn_actualizar.setProperty("class", "btn-neutral")
        self.btn_actualizar.setIcon(qta.icon("mdi6.refresh", color="#FFFFFF"))
        self.btn_actualizar.setIconSize(QSize(16, 16))
        self.btn_actualizar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_actualizar.setMinimumHeight(48)
        self.btn_actualizar.clicked.connect(self.actualizar)
        barra.addWidget(self.btn_actualizar)
        layout.addLayout(barra)

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("color: #3D3D3D; margin: 4px 0px;")
        layout.addWidget(separador)

        self.tabla = TablaEstilizada(self)
        self.tabla.fila_seleccionada.connect(self._set_id)
        self.tabla.cellDoubleClicked.connect(lambda *_: self._editar())
        layout.addWidget(self.tabla, 1)

    def _set_id(self, producto_id: str):
        self.id_seleccionado = producto_id

    def _combo_categorias(self):
        self.combo_categoria.blockSignals(True)
        actual = self.combo_categoria.currentText()
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas")
        self.combo_categoria.addItems(self.controller.obtener_categorias())
        idx = self.combo_categoria.findText(actual)
        self.combo_categoria.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_categoria.blockSignals(False)

    def _cargar_tabla(self, productos):
        datos = [
            {
                "ID": p.id,
                "NOMBRE": p.nombre,
                "PRECIO": f"S/ {float(p.precio):.2f}",
                "CATEGORÍA": p.categoria or "",
                "STOCK": int(p.stock),
                "ESTADO": p.estado_stock(),
            }
            for p in productos
        ]

        def _tag(row: dict) -> str:
            if row["ESTADO"] == "SIN STOCK":
                return "critico"
            if row["ESTADO"] == "STOCK CRITICO":
                return "advertencia"
            return ""

        self.tabla.cargar_datos(datos, _tag)

    def _filtrar_lista(self, productos):
        texto = self.input_buscar.text().strip().lower()
        categoria = self.combo_categoria.currentText().strip()
        filtrados = []
        for p in productos:
            if texto and texto not in (p.nombre or "").lower():
                continue
            if categoria and categoria != "Todas" and (p.categoria or "") != categoria:
                continue
            filtrados.append(p)
        return filtrados

    def _aplicar_filtros(self):
        try:
            productos = self.controller.listar()
            self._cargar_tabla(self._filtrar_lista(productos))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _proveedores_combo(self) -> list[str]:
        return [f"{p.id} - {p.nombre}" for p in self.proveedor_controller.listar()]

    def _agregar(self):
        try:
            dialog = _ProductoDialog(
                self,
                "Agregar Producto",
                self.controller.obtener_categorias(),
                self._proveedores_combo(),
                proximo_id=self.controller.previsualizar_id(),
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            data = dialog.datos()
            producto = Producto(
                None,
                data["nombre"],
                data["precio"],
                data["categoria"] or None,
                data["stock"],
                data["descripcion"] or None,
                data["stock_minimo"],
                data["proveedor_id"] or None,
            )
            self.controller.agregar(producto)
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _editar(self):
        if not self.id_seleccionado:
            QMessageBox.information(self, "Información", "Seleccione un producto para editar")
            return
        try:
            producto = self.controller.buscar(self.id_seleccionado)
            dialog = _ProductoDialog(
                self,
                "Editar Producto",
                self.controller.obtener_categorias(),
                self._proveedores_combo(),
                producto.to_dict(),
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            data = dialog.datos()
            actualizado = Producto(
                data["id"],
                data["nombre"],
                data["precio"],
                data["categoria"] or None,
                data["stock"],
                data["descripcion"] or None,
                data["stock_minimo"],
                data["proveedor_id"] or None,
            )
            self.controller.actualizar(actualizado)
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _eliminar(self):
        if not self.id_seleccionado:
            QMessageBox.information(self, "Información", "Seleccione un producto para eliminar")
            return
        confirmar = QMessageBox.question(
            self,
            "Confirmación",
            f"¿Desea eliminar el producto {self.id_seleccionado}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmar != QMessageBox.StandardButton.Yes:
            return
        try:
            self.controller.eliminar(self.id_seleccionado)
            QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def actualizar(self):
        try:
            self._combo_categorias()
            self._aplicar_filtros()
            self.id_seleccionado = ""
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
