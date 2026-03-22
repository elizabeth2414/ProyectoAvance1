"""Vista de proveedores en PyQt6 con CRUD."""

import sqlite3
import re

from PyQt6.QtCore import QSize, Qt, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from controladores.proveedor_controller import ProveedorController
from modelos.proveedor import Proveedor
from vistas.componentes.tabla import TablaEstilizada
from vistas.estilos.colores import *
from vistas.estilos.qss import get_global_stylesheet


def _capitalizar_nombre(nombre: str) -> str:
    """Capitaliza cada palabra del nombre."""
    return ' '.join(word.capitalize() for word in nombre.split())


def _validar_nombre(nombre: str) -> bool:
    """Valida que el nombre solo contenga letras y espacios."""
    return bool(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre.strip()))


def _validar_correo(correo: str) -> bool:
    """Valida que el correo sea válido y termine en .com o .ec."""
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|ec)$"
    return bool(re.match(patron, correo.strip()))


def _validar_telefono(telefono: str) -> bool:
    """Valida que el teléfono tenga 7 o 10 dígitos."""
    solo_digitos = re.sub(r"\D", "", telefono.strip())
    return len(solo_digitos) in [7, 10]


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
    "Agregar Proveedor": ("fa6s.truck-ramp-box", PRIMARY),
    "Editar Proveedor": ("fa6s.truck", PRIMARY),
}


def _centrar_dialogo(dialog: QDialog):
    """Centra un diálogo en el centro de la pantalla."""
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen:
        geom = screen.availableGeometry()
        dialog_geom = dialog.geometry()
        x = (geom.width() - dialog_geom.width()) // 2 + geom.x()
        y = (geom.height() - dialog_geom.height()) // 2 + geom.y()
        dialog.move(x, y)


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


class _ProveedorDialog(QDialog):
    def __init__(self, parent, titulo: str, datos: dict | None = None, proximo_id: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(520, 320)
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
        
        # Nombre: solo letras, capitalizar automáticamente
        self.input_nombre = QLineEdit(data.get("nombre", ""))
        self.input_nombre.textChanged.connect(self._filtrar_nombre)
        
        # Teléfono: solo 7 o 10 dígitos
        self.input_telefono = QLineEdit(data.get("telefono", ""))
        
        # Correo con validación .com o .ec
        self.input_correo = QLineEdit(data.get("correo", ""))
        
        self.input_direccion = QLineEdit(data.get("direccion", ""))
        self.input_nombre.setPlaceholderText("Ej.: Distribuidora Central")
        self.input_telefono.setPlaceholderText("Ej.: 0968364154 o +51 999 123456")
        self.input_correo.setPlaceholderText("Ej.: contacto@proveedor.com")
        self.input_direccion.setPlaceholderText("Ej.: Calle Comercio 456")

        tel_validator = QRegularExpressionValidator(QRegularExpression(r"[\d\-\+\(\) ]{0,20}"))
        self.input_telefono.setValidator(tel_validator)

        form.addRow("ID:", _campo_con_icono("mdi6.identifier", self.input_id))
        form.addRow("Nombre *:", _campo_con_icono("mdi6.account", self.input_nombre))
        form.addRow("Teléfono:", _campo_con_icono("mdi6.phone", self.input_telefono))
        form.addRow("Correo:", _campo_con_icono("mdi6.email", self.input_correo))
        form.addRow("Dirección:", _campo_con_icono("mdi6.map-marker", self.input_direccion))
        layout.addLayout(form)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {DANGER};")
        layout.addWidget(self.lbl_error)

        fila = QHBoxLayout()
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
        fila.addWidget(btn_cancelar)
        fila.addWidget(btn_guardar)
        layout.addLayout(fila)

    def _filtrar_nombre(self, texto: str):
        """Filtra el nombre: solo letras y espacios, capitaliza automáticamente."""
        texto_filtrado = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", texto)
        if texto_filtrado != texto:
            self.input_nombre.blockSignals(True)
            self.input_nombre.setText(texto_filtrado)
            self.input_nombre.blockSignals(False)

    def _validar(self):
        nombre = self.input_nombre.text().strip()
        correo = self.input_correo.text().strip()
        telefono = self.input_telefono.text().strip()
        
        # Validar nombre
        if not nombre:
            self.lbl_error.setText("❌ El nombre es obligatorio")
            return
        
        if not _validar_nombre(nombre):
            self.lbl_error.setText("❌ El nombre solo puede contener letras y espacios")
            return
        
        # Validar correo (si se proporciona)
        if correo and not _validar_correo(correo):
            self.lbl_error.setText("❌ El correo debe ser válido y terminar en .com o .ec")
            return
        
        # Validar teléfono (si se proporciona)
        if telefono and not _validar_telefono(telefono):
            self.lbl_error.setText("❌ El teléfono debe tener 7 o 10 dígitos")
            return
        
        # Capitalizar el nombre
        self.input_nombre.setText(_capitalizar_nombre(nombre))
        self.lbl_error.setText("")
        self.accept()

    def datos(self) -> dict:
        return {
            "id": self.input_id.text().strip(),
            "nombre": self.input_nombre.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "correo": self.input_correo.text().strip(),
            "direccion": self.input_direccion.text().strip(),
        }


class VistaProveedores(QWidget):
    """Gestión de proveedores con búsqueda y CRUD."""

    def __init__(self, parent, conexion: sqlite3.Connection, usuario):
        super().__init__(parent)
        self.conexion = conexion
        self.usuario = usuario
        self.controller = ProveedorController(conexion)
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
        top.addWidget(_crear_titulo("fa6s.truck", "Gestión de Proveedores", PRIMARY))

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por nombre...")
        self.input_buscar.setMinimumWidth(200)
        self.input_buscar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_buscar.textChanged.connect(self._buscar_tiempo_real)
        top.addWidget(self.input_buscar, 1)
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

    def _set_id(self, proveedor_id: str):
        self.id_seleccionado = proveedor_id

    def _cargar_tabla(self, proveedores):
        datos = [
            {
                "ID": p.id,
                "NOMBRE": p.nombre,
                "TELÉFONO": p.telefono or "",
                "CORREO": p.correo or "",
                "DIRECCIÓN": p.direccion or "",
            }
            for p in proveedores
        ]
        self.tabla.cargar_datos(datos)

    def _buscar_tiempo_real(self):
        try:
            texto = self.input_buscar.text().strip()
            if texto:
                self._cargar_tabla(self.controller.buscar_por_nombre(texto))
            else:
                self._cargar_tabla(self.controller.listar())
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _agregar(self):
        dialog = _ProveedorDialog(self, "Agregar Proveedor", proximo_id=self.controller.previsualizar_id())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            data = dialog.datos()
            id_value = data["id"]
            proveedor = Proveedor(
                None if id_value in ("Automático", "Automatico", "") else id_value,
                data["nombre"],
                data["telefono"],
                data["correo"],
                data["direccion"],
            )
            self.controller.agregar(proveedor)
            QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _editar(self):
        if not self.id_seleccionado:
            QMessageBox.information(self, "Información", "Seleccione un proveedor para editar")
            return
        try:
            proveedor = self.controller.buscar(self.id_seleccionado)
            dialog = _ProveedorDialog(self, "Editar Proveedor", proveedor.to_dict())
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            data = dialog.datos()
            actualizado = Proveedor(data["id"], data["nombre"], data["telefono"], data["correo"], data["direccion"])
            self.controller.actualizar(actualizado)
            QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _eliminar(self):
        if not self.id_seleccionado:
            QMessageBox.information(self, "Información", "Seleccione un proveedor para eliminar")
            return
        confirmar = QMessageBox.question(
            self,
            "Confirmación",
            f"¿Desea eliminar el proveedor {self.id_seleccionado}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmar != QMessageBox.StandardButton.Yes:
            return
        try:
            self.controller.eliminar(self.id_seleccionado)
            QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente")
            self.actualizar()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def actualizar(self):
        try:
            self._cargar_tabla(self.controller.listar())
            self.id_seleccionado = ""
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
