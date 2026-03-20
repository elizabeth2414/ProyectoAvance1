"""
Controlador de Proveedores - Gestiona operaciones CRUD con SQLite
"""
import sqlite3
from typing import List, Optional
from modelos.proveedor import Proveedor
from modelos.excepciones import (
    ProveedorNoEncontradoError,
    DuplicadoError,
    ValidacionError
)


class ProveedorController:
    """Controlador para gestionar operaciones de proveedores"""

    def __init__(self, conexion: sqlite3.Connection):
        self.conn = conexion

    def _generar_id(self) -> str:
        """Genera un nuevo ID para proveedor consultando el último ID en BD"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM proveedores ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()

        if resultado:
            ultimo_id = resultado['id']
            numero = int(ultimo_id.split('-')[1]) + 1
        else:
            numero = 1

        return f"PRV-{numero:03d}"

    def previsualizar_id(self) -> str:
        """Retorna el próximo ID disponible para mostrar en formularios."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM proveedores ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        if resultado:
            numero = int(resultado['id'].split('-')[1]) + 1
        else:
            numero = 1
        return f"PRV-{numero:03d}"

    def agregar(self, proveedor: Proveedor) -> Proveedor:
        """Agrega un nuevo proveedor a la base de datos"""
        if not proveedor.nombre:
            raise ValidacionError("nombre", "El nombre es obligatorio")

        if not proveedor.id:
            proveedor.id = self._generar_id()

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO proveedores (id, nombre, telefono, correo, direccion)
                VALUES (?, ?, ?, ?, ?)
            """, (
                proveedor.id,
                proveedor.nombre,
                proveedor.telefono,
                proveedor.correo,
                proveedor.direccion
            ))
            self.conn.commit()
            return proveedor

        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise DuplicadoError("Proveedor", proveedor.id)

    def buscar(self, proveedor_id: str) -> Proveedor:
        """Busca un proveedor por su ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM proveedores WHERE id = ?", (proveedor_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise ProveedorNoEncontradoError(proveedor_id)

        return Proveedor.from_row(resultado)

    def buscar_por_nombre(self, nombre: str) -> List[Proveedor]:
        """Busca proveedores por nombre (búsqueda parcial)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM proveedores WHERE nombre LIKE ?",
            (f"%{nombre}%",)
        )
        resultados = cursor.fetchall()
        return [Proveedor.from_row(row) for row in resultados]

    def actualizar(self, proveedor: Proveedor) -> Proveedor:
        """Actualiza los datos de un proveedor existente"""
        if not proveedor.id:
            raise ValidacionError("id", "El ID es obligatorio para actualizar")

        self.buscar(proveedor.id)

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE proveedores
            SET nombre = ?, telefono = ?, correo = ?, direccion = ?
            WHERE id = ?
        """, (
            proveedor.nombre,
            proveedor.telefono,
            proveedor.correo,
            proveedor.direccion,
            proveedor.id
        ))
        self.conn.commit()
        return proveedor

    def eliminar(self, proveedor_id: str) -> bool:
        """Elimina un proveedor de la base de datos"""
        self.buscar(proveedor_id)

        cursor = self.conn.cursor()

        # Verificar si tiene productos asociados
        cursor.execute(
            "SELECT COUNT(*) FROM productos WHERE proveedor_id = ?",
            (proveedor_id,)
        )
        if cursor.fetchone()[0] > 0:
            raise ValidacionError(
                "proveedor_id",
                "No se puede eliminar: el proveedor tiene productos asociados"
            )

        cursor.execute("DELETE FROM proveedores WHERE id = ?", (proveedor_id,))
        self.conn.commit()
        return True

    def listar(self) -> List[Proveedor]:
        """Lista todos los proveedores"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM proveedores ORDER BY nombre")
        resultados = cursor.fetchall()
        return [Proveedor.from_row(row) for row in resultados]

    def contar(self) -> int:
        """Retorna el número total de proveedores"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM proveedores")
        return cursor.fetchone()[0]

    def obtener_productos(self, proveedor_id: str) -> List:
        """Obtiene los productos de un proveedor"""
        self.buscar(proveedor_id)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE proveedor_id = ?",
            (proveedor_id,)
        )
        return cursor.fetchall()
