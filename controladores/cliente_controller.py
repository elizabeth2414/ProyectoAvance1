"""
Controlador de Clientes - Gestiona operaciones CRUD con SQLite
"""
import sqlite3
from typing import List, Optional
from modelos.cliente import Cliente
from modelos.excepciones import (
    ClienteNoEncontradoError,
    DuplicadoError,
    ValidacionError
)


class ClienteController:
    """Controlador para gestionar operaciones de clientes"""

    def __init__(self, conexion: sqlite3.Connection):
        self.conn = conexion

    def _generar_id(self) -> str:
        """Genera un nuevo ID para cliente consultando el último ID en BD"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clientes ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()

        if resultado:
            ultimo_id = resultado['id']
            # Extraer número y incrementar
            numero = int(ultimo_id.split('-')[1]) + 1
        else:
            numero = 1

        return f"CLI-{numero:03d}"

    def previsualizar_id(self) -> str:
        """Retorna el próximo ID disponible para mostrar en formularios."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clientes ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        if resultado:
            numero = int(resultado['id'].split('-')[1]) + 1
        else:
            numero = 1
        return f"CLI-{numero:03d}"

    def agregar(self, cliente: Cliente) -> Cliente:
        """Agrega un nuevo cliente a la base de datos"""
        if not cliente.nombre:
            raise ValidacionError("nombre", "El nombre es obligatorio")

        # Generar ID si no tiene
        if not cliente.id:
            cliente.id = self._generar_id()

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO clientes (id, nombre, correo, telefono, direccion)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cliente.id,
                cliente.nombre,
                cliente.correo,
                cliente.telefono,
                cliente.direccion
            ))
            self.conn.commit()
            return cliente

        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise DuplicadoError("Cliente", cliente.id)

    def buscar(self, cliente_id: str) -> Cliente:
        """Busca un cliente por su ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise ClienteNoEncontradoError(cliente_id)

        return Cliente.from_row(resultado)

    def buscar_por_nombre(self, nombre: str) -> List[Cliente]:
        """Busca clientes por nombre (búsqueda parcial)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM clientes WHERE nombre LIKE ?",
            (f"%{nombre}%",)
        )
        resultados = cursor.fetchall()
        return [Cliente.from_row(row) for row in resultados]

    def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza los datos de un cliente existente"""
        if not cliente.id:
            raise ValidacionError("id", "El ID es obligatorio para actualizar")

        # Verificar que existe
        self.buscar(cliente.id)

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nombre = ?, correo = ?, telefono = ?, direccion = ?
            WHERE id = ?
        """, (
            cliente.nombre,
            cliente.correo,
            cliente.telefono,
            cliente.direccion,
            cliente.id
        ))
        self.conn.commit()
        return cliente

    def eliminar(self, cliente_id: str) -> bool:
        """Elimina un cliente de la base de datos"""
        # Verificar que existe
        self.buscar(cliente_id)

        cursor = self.conn.cursor()

        # Verificar si tiene ventas asociadas
        cursor.execute(
            "SELECT COUNT(*) FROM ventas WHERE cliente_id = ?",
            (cliente_id,)
        )
        if cursor.fetchone()[0] > 0:
            raise ValidacionError(
                "cliente_id",
                "No se puede eliminar: el cliente tiene ventas asociadas"
            )

        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        self.conn.commit()
        return True

    def listar(self) -> List[Cliente]:
        """Lista todos los clientes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nombre")
        resultados = cursor.fetchall()
        return [Cliente.from_row(row) for row in resultados]

    def contar(self) -> int:
        """Retorna el número total de clientes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes")
        return cursor.fetchone()[0]

    def obtener_historial_compras(self, cliente_id: str) -> List:
        """Obtiene el historial de compras de un cliente"""
        # Verificar que existe
        self.buscar(cliente_id)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.*, p.nombre as producto_nombre, p.precio
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.cliente_id = ?
            ORDER BY v.fecha DESC
        """, (cliente_id,))

        return cursor.fetchall()
