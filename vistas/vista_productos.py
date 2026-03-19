"""
Vista Productos - CRUD de productos (Versión Simplificada)
"""
import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from typing import Optional, List

from .componentes.tabla import TablaPersonalizada
from controladores.producto_controller import ProductoController
from modelos.producto import Producto


class VistaProductos(ctk.CTkFrame):
    """Vista CRUD de productos"""

    def __init__(
        self,
        parent,
        conexion: sqlite3.Connection,
        usuario,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.conexion = conexion
        self.usuario = usuario
        self.controller = ProductoController(conexion)
        self.producto_seleccionado: Optional[str] = None

        self._crear_widgets()
        self.actualizar()

    def _crear_widgets(self):
        """Crea los widgets de la vista"""
        # Frame superior
        self.frame_superior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_superior.pack(fill="x", pady=(0, 10))

        # Titulo
        self.lbl_titulo = ctk.CTkLabel(
            self.frame_superior,
            text="Gestion de Productos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_titulo.pack(side="left")

        # Buscador
        self.frame_busqueda = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        self.frame_busqueda.pack(side="right")

        self.entry_buscar = ctk.CTkEntry(
            self.frame_busqueda,
            width=250,
            height=35,
            placeholder_text="Buscar por nombre..."
        )
        self.entry_buscar.pack(side="left", padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self._buscar)

        self.btn_buscar = ctk.CTkButton(
            self.frame_busqueda,
            text="Buscar",
            width=80,
            height=35,
            command=self._buscar
        )
        self.btn_buscar.pack(side="left")

        # Frame botones CRUD
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(fill="x", pady=(0, 10))

        self.btn_agregar = ctk.CTkButton(
            self.frame_botones,
            text="+ Agregar",
            width=100,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            command=self._abrir_formulario_agregar
        )
        self.btn_agregar.pack(side="left", padx=(0, 5))

        self.btn_editar = ctk.CTkButton(
            self.frame_botones,
            text="Editar",
            width=100,
            height=35,
            fg_color="#007bff",
            hover_color="#0056b3",
            command=self._abrir_formulario_editar
        )
        self.btn_editar.pack(side="left", padx=(0, 5))

        self.btn_eliminar = ctk.CTkButton(
            self.frame_botones,
            text="Eliminar",
            width=100,
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self._eliminar
        )
        self.btn_eliminar.pack(side="left", padx=(0, 5))

        if not self.usuario.es_admin():
            self.btn_eliminar.configure(state="disabled")

        self.btn_actualizar = ctk.CTkButton(
            self.frame_botones,
            text="Actualizar",
            width=100,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.actualizar
        )
        self.btn_actualizar.pack(side="left")

        # Filtro categoria
        self.lbl_filtro = ctk.CTkLabel(
            self.frame_botones,
            text="Categoria:",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_filtro.pack(side="left", padx=(20, 5))

        self.combo_categoria = ctk.CTkComboBox(
            self.frame_botones,
            width=150,
            height=35,
            values=["Todos"],
            command=self._filtrar_categoria
        )
        self.combo_categoria.pack(side="left")
        self.combo_categoria.set("Todos")

        # Tabla
        self.tabla = TablaPersonalizada(
            self,
            columnas=[
                ("id", "ID", 80),
                ("nombre", "Nombre", 180),
                ("precio", "Precio", 100),
                ("categoria", "Categoria", 120),
                ("stock", "Stock", 70),
                ("estado", "Estado", 100)
            ],
            on_select=self._on_seleccionar,
            on_double_click=self._on_doble_clic
        )
        self.tabla.pack(fill="both", expand=True)

    def _buscar(self, event=None):
        """Busca productos por nombre"""
        texto = self.entry_buscar.get().strip()
        if texto:
            productos = self.controller.buscar_por_nombre(texto)
        else:
            productos = self.controller.listar()
        self._cargar_tabla(productos)

    def _filtrar_categoria(self, categoria: str):
        """Filtra productos por categoria"""
        if categoria == "Todos":
            productos = self.controller.listar()
        else:
            productos = self.controller.buscar_por_categoria(categoria)
        self._cargar_tabla(productos)

    def _cargar_tabla(self, productos: List[Producto]):
        """Carga los productos en la tabla"""
        datos = []
        for prod in productos:
            estado = prod.estado_stock()
            datos.append((
                prod.id,
                prod.nombre,
                f"S/ {prod.precio:.2f}",
                prod.categoria or "",
                prod.stock,
                estado
            ))

        def obtener_tag(fila):
            estado = fila[5]
            if estado == "SIN STOCK":
                return "critico"
            elif estado == "STOCK CRITICO":
                return "advertencia"
            return "normal"

        self.tabla.cargar_datos(datos, obtener_tag)

    def _actualizar_categorias(self):
        """Actualiza el combo de categorias"""
        categorias = ["Todos"] + self.controller.obtener_categorias()
        self.combo_categoria.configure(values=categorias)

    def actualizar(self):
        """Actualiza la tabla con todos los productos"""
        productos = self.controller.listar()
        self._cargar_tabla(productos)
        self._actualizar_categorias()
        self.producto_seleccionado = None

    def _on_seleccionar(self, item_id: str):
        """Maneja la seleccion de una fila"""
        self.producto_seleccionado = self.tabla.obtener_id_seleccion()

    def _on_doble_clic(self, item_id: str):
        """Maneja el doble clic para editar"""
        self._abrir_formulario_editar()

    def _abrir_formulario_agregar(self):
        """Abre un formulario simple para agregar producto"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Producto")
        ventana.geometry("500x550")
        ventana.resizable(False, False)

        # Campos
        ctk.CTkLabel(ventana, text="Nombre:", font=ctk.CTkFont(size=12)).pack(pady=(15, 0), padx=20, anchor="w")
        entry_nombre = ctk.CTkEntry(ventana, width=450)
        entry_nombre.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Precio (S/):", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_precio = ctk.CTkEntry(ventana, width=450)
        entry_precio.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Categoria:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_categoria = ctk.CTkEntry(ventana, width=450)
        entry_categoria.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Stock:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_stock = ctk.CTkEntry(ventana, width=450)
        entry_stock.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Stock Minimo:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_stock_minimo = ctk.CTkEntry(ventana, width=450)
        entry_stock_minimo.insert(0, "5")
        entry_stock_minimo.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Descripcion:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_desc = ctk.CTkEntry(ventana, width=450)
        entry_desc.pack(pady=5, padx=20)

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                precio = float(entry_precio.get().strip())
                categoria = entry_categoria.get().strip()
                stock = int(entry_stock.get().strip())
                stock_minimo = int(entry_stock_minimo.get().strip())
                descripcion = entry_desc.get().strip()

                if not nombre or precio <= 0 or stock < 0:
                    messagebox.showwarning("Validacion", "Complete los campos requeridos correctamente")
                    return

                producto = Producto(
                    id=None,
                    nombre=nombre,
                    precio=precio,
                    categoria=categoria if categoria else None,
                    stock=stock,
                    stock_minimo=stock_minimo,
                    descripcion=descripcion if descripcion else None,
                    proveedor_id=None
                )
                self.controller.agregar(producto)
                messagebox.showinfo("Exito", "Producto agregado correctamente")
                ventana.destroy()
                self.actualizar()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear: {str(e)}")

        # Frame para botones
        frame_botones = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_botones.pack(pady=20, padx=20, fill="x")

        ctk.CTkButton(
            frame_botones,
            text="Guardar",
            width=220,
            height=40,
            fg_color="#28a745",
            hover_color="#218838",
            command=guardar
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            width=220,
            height=40,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=ventana.destroy
        ).pack(side="left", padx=(5, 0))

    def _abrir_formulario_editar(self):
        """Abre un formulario simple para editar producto"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Atencion", "Seleccione un producto para editar")
            return

        try:
            producto = self.controller.buscar(self.producto_seleccionado)
            if not producto:
                messagebox.showerror("Error", "Producto no encontrado")
                return

            ventana = ctk.CTkToplevel(self)
            ventana.title(f"Editar Producto - {producto.nombre}")
            ventana.geometry("500x600")
            ventana.resizable(False, False)

            # Campos
            ctk.CTkLabel(ventana, text="ID:", font=ctk.CTkFont(size=12)).pack(pady=(15, 0), padx=20, anchor="w")
            entry_id = ctk.CTkEntry(ventana, width=450)
            entry_id.insert(0, str(producto.id))
            entry_id.configure(state="disabled")
            entry_id.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Nombre:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_nombre = ctk.CTkEntry(ventana, width=450)
            entry_nombre.insert(0, producto.nombre)
            entry_nombre.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Precio (S/):", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_precio = ctk.CTkEntry(ventana, width=450)
            entry_precio.insert(0, str(producto.precio))
            entry_precio.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Categoria:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_categoria = ctk.CTkEntry(ventana, width=450)
            entry_categoria.insert(0, producto.categoria or "")
            entry_categoria.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Stock:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_stock = ctk.CTkEntry(ventana, width=450)
            entry_stock.insert(0, str(producto.stock))
            entry_stock.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Stock Minimo:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_stock_minimo = ctk.CTkEntry(ventana, width=450)
            entry_stock_minimo.insert(0, str(producto.stock_minimo))
            entry_stock_minimo.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Descripcion:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_desc = ctk.CTkEntry(ventana, width=450)
            entry_desc.insert(0, producto.descripcion or "")
            entry_desc.pack(pady=5, padx=20)

            def guardar():
                try:
                    nombre = entry_nombre.get().strip()
                    precio = float(entry_precio.get().strip())
                    categoria = entry_categoria.get().strip()
                    stock = int(entry_stock.get().strip())
                    stock_minimo = int(entry_stock_minimo.get().strip())
                    descripcion = entry_desc.get().strip()

                    if not nombre or precio <= 0 or stock < 0:
                        messagebox.showwarning("Validacion", "Complete los campos requeridos correctamente")
                        return

                    producto.nombre = nombre
                    producto.precio = precio
                    producto.categoria = categoria if categoria else None
                    producto.stock = stock
                    producto.stock_minimo = stock_minimo
                    producto.descripcion = descripcion if descripcion else None

                    self.controller.actualizar(producto)
                    messagebox.showinfo("Exito", "Producto actualizado correctamente")
                    ventana.destroy()
                    self.actualizar()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar: {str(e)}")

            # Frame para botones
            frame_botones = ctk.CTkFrame(ventana, fg_color="transparent")
            frame_botones.pack(pady=20, padx=20, fill="x")

            ctk.CTkButton(
                frame_botones,
                text="Guardar",
                width=220,
                height=40,
                fg_color="#007bff",
                hover_color="#0056b3",
                command=guardar
            ).pack(side="left", padx=(0, 5))

            ctk.CTkButton(
                frame_botones,
                text="Cancelar",
                width=220,
                height=40,
                fg_color="#6c757d",
                hover_color="#5a6268",
                command=ventana.destroy
            ).pack(side="left", padx=(5, 0))

        except Exception as e:
            messagebox.showerror("Error", f"Error al editar: {str(e)}")

    def _eliminar(self):
        """Elimina el producto seleccionado"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Atencion", "Seleccione un producto para eliminar")
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"Desea eliminar el producto {self.producto_seleccionado}?"
        ):
            return

        try:
            self.controller.eliminar(self.producto_seleccionado)
            messagebox.showinfo("Exito", "Producto eliminado correctamente")
            self.actualizar()
        except Exception as e:
            messagebox.showerror("Error", str(e))
