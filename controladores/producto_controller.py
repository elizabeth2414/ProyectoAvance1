"""
Controlador de Productos - Gestiona operaciones CRUD con SQLite
"""
import sqlite3
from typing import List, Optional
from modelos.producto import Producto
from modelos.excepciones import (
    ProductoNoEncontradoError,
    DuplicadoError,
    ValidacionError,
    StockInsuficienteError
)


class ProductoController:
    """Controlador para gestionar operaciones de productos"""

    def __init__(self, conexion: sqlite3.Connection):
        self.conn = conexion

    def _generar_id(self) -> str:
        """Genera un nuevo ID para producto consultando el último ID en BD"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM productos ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()

        if resultado:
            ultimo_id = resultado['id']
            numero = int(ultimo_id.split('-')[1]) + 1
        else:
            numero = 1

        return f"PRD-{numero:03d}"

    def agregar(self, producto: Producto) -> Producto:
        """Agrega un nuevo producto a la base de datos"""
        if not producto.nombre:
            raise ValidacionError("nombre", "El nombre es obligatorio")
        if producto.precio < 0:
            raise ValidacionError("precio", "El precio no puede ser negativo")

        if not producto.id:
            producto.id = self._generar_id()

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO productos
                (id, nombre, precio, categoria, stock, descripcion, stock_minimo, proveedor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                producto.id,
                producto.nombre,
                producto.precio,
                producto.categoria,
                producto.stock,
                producto.descripcion,
                producto.stock_minimo,
                producto.proveedor_id
            ))
            self.conn.commit()
            return producto

        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise DuplicadoError("Producto", producto.id)

    def buscar(self, producto_id: str) -> Producto:
        """Busca un producto por su ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise ProductoNoEncontradoError(producto_id)

        return Producto.from_row(resultado)

    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        """Busca productos por nombre (búsqueda parcial)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE ?",
            (f"%{nombre}%",)
        )
        resultados = cursor.fetchall()
        return [Producto.from_row(row) for row in resultados]

    def buscar_por_categoria(self, categoria: str) -> List[Producto]:
        """Busca productos por categoría"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE categoria = ?",
            (categoria,)
        )
        resultados = cursor.fetchall()
        return [Producto.from_row(row) for row in resultados]

    def actualizar(self, producto: Producto) -> Producto:
        """Actualiza los datos de un producto existente"""
        if not producto.id:
            raise ValidacionError("id", "El ID es obligatorio para actualizar")

        self.buscar(producto.id)

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre = ?, precio = ?, categoria = ?, stock = ?,
                descripcion = ?, stock_minimo = ?, proveedor_id = ?
            WHERE id = ?
        """, (
            producto.nombre,
            producto.precio,
            producto.categoria,
            producto.stock,
            producto.descripcion,
            producto.stock_minimo,
            producto.proveedor_id,
            producto.id
        ))
        self.conn.commit()
        return producto

    def eliminar(self, producto_id: str) -> bool:
        """Elimina un producto de la base de datos"""
        self.buscar(producto_id)

        cursor = self.conn.cursor()

        # Verificar si tiene ventas asociadas
        cursor.execute(
            "SELECT COUNT(*) FROM ventas WHERE producto_id = ?",
            (producto_id,)
        )
        if cursor.fetchone()[0] > 0:
            raise ValidacionError(
                "producto_id",
                "No se puede eliminar: el producto tiene ventas asociadas"
            )

        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        self.conn.commit()
        return True

    def listar(self) -> List[Producto]:
        """Lista todos los productos"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        resultados = cursor.fetchall()
        return [Producto.from_row(row) for row in resultados]

    def listar_stock_critico(self) -> List[Producto]:
        """Lista productos con stock crítico (stock < stock_minimo)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE stock < stock_minimo ORDER BY stock"
        )
        resultados = cursor.fetchall()
        return [Producto.from_row(row) for row in resultados]

    def reducir_stock(self, producto_id: str, cantidad: int) -> Producto:
        """Reduce el stock de un producto"""
        producto = self.buscar(producto_id)

        if producto.stock < cantidad:
            raise StockInsuficienteError(producto_id, producto.stock, cantidad)

        producto.stock -= cantidad
        return self.actualizar(producto)

    def aumentar_stock(self, producto_id: str, cantidad: int) -> Producto:
        """Aumenta el stock de un producto"""
        producto = self.buscar(producto_id)
        producto.stock += cantidad
        return self.actualizar(producto)

    def contar(self) -> int:
        """Retorna el número total de productos"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        return cursor.fetchone()[0]

    def obtener_categorias(self) -> List[str]:
        """Obtiene lista de categorías únicas"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT DISTINCT categoria FROM productos WHERE categoria IS NOT NULL"
        )
        return [row[0] for row in cursor.fetchall()]
