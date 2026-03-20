"""Dialogo base para formularios modernos en PyQt6."""

from typing import Any

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)


class FormularioDialogo(QDialog):
    """Formulario reusable basado en QDialog y QFormLayout."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(460, 320)
        self._campos = {}

        self._layout = QVBoxLayout(self)
        self._form = QFormLayout()
        self._form.setLabelAlignment(self._form.labelAlignment())
        self._form.setContentsMargins(0, 0, 0, 0)
        self._form.setSpacing(10)
        self._layout.addLayout(self._form)

        self._botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self._botones.accepted.connect(self.accept)
        self._botones.rejected.connect(self.reject)
        self._layout.addWidget(self._botones)

    def agregar_campo_texto(self, nombre: str, etiqueta: str, valor: str = "", password: bool = False):
        campo = QLineEdit(valor)
        if password:
            campo.setEchoMode(QLineEdit.EchoMode.Password)
        self._campos[nombre] = campo
        self._form.addRow(etiqueta, campo)
        return campo

    def agregar_combo(self, nombre: str, etiqueta: str, opciones: list[str], valor: str = ""):
        combo = QComboBox()
        combo.addItems(opciones)
        if valor:
            combo.setCurrentText(valor)
        self._campos[nombre] = combo
        self._form.addRow(etiqueta, combo)
        return combo

    def agregar_texto_largo(self, nombre: str, etiqueta: str, valor: str = ""):
        area = QTextEdit(valor)
        area.setMinimumHeight(90)
        self._campos[nombre] = area
        self._form.addRow(etiqueta, area)
        return area

    def obtener_valores(self) -> dict[str, Any]:
        valores = {}
        for nombre, widget in self._campos.items():
            if isinstance(widget, QLineEdit):
                valores[nombre] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                valores[nombre] = widget.currentText().strip()
            elif isinstance(widget, QTextEdit):
                valores[nombre] = widget.toPlainText().strip()
        return valores
