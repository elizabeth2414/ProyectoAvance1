"""Tabla Material Design para PyQt6."""

from typing import Callable, Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QSizePolicy, QTableWidget, QTableWidgetItem


class TablaEstilizada(QTableWidget):
    """QTableWidget con estilo oscuro y manejo de tags por fila."""

    fila_seleccionada = pyqtSignal(str)

    TAGS = {
        "critico": ("#8B0000", "#FFFFFF"),
        "advertencia": ("#7B4500", "#FFFFFF"),
        "devuelta": ("#3D3D3D", "#A0A0A0"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.horizontalHeader().setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._datos_cache = []
        self._tag_cache = None
        self._col_orden = 0
        self._orden_asc = True

        self.horizontalHeader().sectionClicked.connect(self._ordenar_columna)
        self.itemSelectionChanged.connect(self._emitir_fila_seleccionada)

    def cargar_datos(self, datos: Iterable, tag_funcion: Callable | None = None):
        self.setSortingEnabled(False)
        datos = list(datos)
        self._datos_cache = datos
        self._tag_cache = tag_funcion
        self._renderizar(datos, tag_funcion)

        self._col_orden = -1
        self._orden_asc = True
        self._ordenar_columna(0)

    def _renderizar(self, datos: list, tag_funcion: Callable | None = None):
        self.clearContents()
        if not datos:
            self.setRowCount(0)
            self.setColumnCount(0)
            return

        if isinstance(datos[0], dict):
            columnas = list(datos[0].keys())
            filas = [
                [str(registro.get(col, "")) if registro.get(col, "") is not None else "" for col in columnas]
                for registro in datos
            ]
            self.setColumnCount(len(columnas))
            self.setHorizontalHeaderLabels([str(c) for c in columnas])
        else:
            filas = [[str(v) if v is not None else "" for v in f] for f in datos]
            columnas = [f"Columna {i + 1}" for i in range(len(filas[0]))]
            self.setColumnCount(len(columnas))
            self.setHorizontalHeaderLabels(columnas)

        self.setRowCount(len(filas))

        for row, fila in enumerate(filas):
            tag = tag_funcion(datos[row]) if tag_funcion else None
            for col, valor in enumerate(fila):
                texto = "" if valor is None else str(valor)
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if tag in self.TAGS:
                    bg, fg = self.TAGS[tag]
                    item.setBackground(QColor(bg))
                    item.setForeground(QColor(fg))
                self.setItem(row, col, item)

        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _ordenar_columna(self, col_idx: int):
        if not self._datos_cache:
            return

        if col_idx == self._col_orden:
            self._orden_asc = not self._orden_asc
        else:
            self._col_orden = col_idx
            self._orden_asc = True

        if isinstance(self._datos_cache[0], dict):
            keys = list(self._datos_cache[0].keys())
            if col_idx >= len(keys):
                return
            key = keys[col_idx]

            def get_val(registro):
                val = registro.get(key, "")
                try:
                    return (0, float(str(val).replace("S/ ", "").replace("%", "")))
                except (ValueError, TypeError):
                    return (1, str(val).lower())
        else:
            def get_val(fila):
                val = fila[col_idx] if col_idx < len(fila) else ""
                try:
                    return (0, float(str(val).replace("S/ ", "").replace("%", "")))
                except (ValueError, TypeError):
                    return (1, str(val).lower())

        datos_ordenados = sorted(self._datos_cache, key=get_val, reverse=not self._orden_asc)

        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(
            col_idx,
            Qt.SortOrder.AscendingOrder if self._orden_asc else Qt.SortOrder.DescendingOrder,
        )

        self._renderizar(datos_ordenados, self._tag_cache)

    def obtener_id_seleccion(self) -> str:
        fila = self.currentRow()
        if fila < 0:
            return ""
        item_id = self.item(fila, 0)
        return item_id.text() if item_id else ""

    def _emitir_fila_seleccionada(self):
        item_id = self.obtener_id_seleccion()
        if item_id:
            self.fila_seleccionada.emit(item_id)
