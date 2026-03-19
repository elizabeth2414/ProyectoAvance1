"""
Tabla personalizada con Treeview estilizado para tema oscuro
"""
import customtkinter as ctk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional, Dict, Any


class TablaPersonalizada(ctk.CTkFrame):
    """Treeview personalizado con estilo oscuro"""

    def __init__(
        self,
        parent,
        columnas: List[Tuple[str, str, int]],  # [(id, texto, ancho), ...]
        on_select: Optional[Callable[[str], None]] = None,
        on_double_click: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.columnas = columnas
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.filas_coloreadas: Dict[str, str] = {}

        self._configurar_estilo()
        self._crear_widgets()

    def _configurar_estilo(self):
        """Configura el estilo oscuro del Treeview"""
        self.style = ttk.Style()

        # Tema oscuro
        self.style.theme_use("clam")

        self.style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            borderwidth=0,
            rowheight=30
        )

        self.style.configure(
            "Treeview.Heading",
            background="#1f538d",
            foreground="white",
            borderwidth=0,
            font=('Segoe UI', 10, 'bold')
        )

        self.style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )

        self.style.map(
            "Treeview.Heading",
            background=[("active", "#2E6DB4")]
        )

        # Estilo del scrollbar
        self.style.configure(
            "Vertical.TScrollbar",
            background="#3b3b3b",
            troughcolor="#2b2b2b",
            borderwidth=0,
            arrowcolor="white"
        )

    def _crear_widgets(self):
        """Crea el Treeview y scrollbars"""
        # Frame contenedor
        self.frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbar vertical
        self.scrollbar_y = ttk.Scrollbar(self.frame_tabla, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        # Scrollbar horizontal
        self.scrollbar_x = ttk.Scrollbar(self.frame_tabla, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        columnas_ids = [col[0] for col in self.columnas]
        self.tree = ttk.Treeview(
            self.frame_tabla,
            columns=columnas_ids,
            show="headings",
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set,
            selectmode="browse"
        )
        self.tree.pack(fill="both", expand=True)

        # Configurar scrollbars
        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)

        # Configurar columnas
        for col_id, col_texto, col_ancho in self.columnas:
            self.tree.heading(col_id, text=col_texto, anchor="w")
            self.tree.column(col_id, width=col_ancho, minwidth=50, anchor="w")

        # Configurar tags para colores
        self.tree.tag_configure("critico", background="#8B0000", foreground="white")
        self.tree.tag_configure("advertencia", background="#CD853F", foreground="white")
        self.tree.tag_configure("devuelta", background="#4a4a4a", foreground="gray")
        self.tree.tag_configure("normal", background="#2b2b2b", foreground="white")
        self.tree.tag_configure("par", background="#333333", foreground="white")
        self.tree.tag_configure("impar", background="#2b2b2b", foreground="white")

        # Eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

    def _on_select(self, event):
        """Maneja seleccion de fila"""
        if self.on_select:
            seleccion = self.tree.selection()
            if seleccion:
                item_id = seleccion[0]
                self.on_select(item_id)

    def _on_double_click(self, event):
        """Maneja doble clic en fila"""
        if self.on_double_click:
            seleccion = self.tree.selection()
            if seleccion:
                item_id = seleccion[0]
                self.on_double_click(item_id)

    def insertar(self, valores: Tuple, tag: str = "normal", id_fila: str = None) -> str:
        """Inserta una fila en la tabla"""
        item_id = self.tree.insert("", "end", values=valores, tags=(tag,), iid=id_fila)
        return item_id

    def limpiar(self):
        """Elimina todas las filas"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def cargar_datos(
        self,
        datos: List[Tuple],
        tag_funcion: Optional[Callable[[Tuple], str]] = None
    ):
        """Carga multiples filas con tags opcionales"""
        self.limpiar()
        for i, fila in enumerate(datos):
            if tag_funcion:
                tag = tag_funcion(fila)
            else:
                tag = "par" if i % 2 == 0 else "impar"
            self.insertar(fila, tag)

    def obtener_seleccion(self) -> Optional[Tuple]:
        """Obtiene los valores de la fila seleccionada"""
        seleccion = self.tree.selection()
        if seleccion:
            return self.tree.item(seleccion[0])["values"]
        return None

    def obtener_id_seleccion(self) -> Optional[str]:
        """Obtiene el ID de la fila seleccionada"""
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion[0])["values"]
            if valores:
                return str(valores[0])
        return None

    def actualizar_fila(self, item_id: str, valores: Tuple, tag: str = "normal"):
        """Actualiza una fila existente"""
        self.tree.item(item_id, values=valores, tags=(tag,))

    def eliminar_fila(self, item_id: str):
        """Elimina una fila especifica"""
        try:
            self.tree.delete(item_id)
        except:
            pass

    def buscar(self, texto: str, columna_idx: int = 1):
        """Resalta filas que coincidan con la busqueda"""
        texto = texto.lower()
        for item in self.tree.get_children():
            valores = self.tree.item(item)["values"]
            if valores and len(valores) > columna_idx:
                if texto in str(valores[columna_idx]).lower():
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    return True
        return False
