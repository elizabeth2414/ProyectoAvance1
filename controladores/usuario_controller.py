"""
Controlador de Usuarios - Gestiona operaciones CRUD con SQLite
"""
import sqlite3
from typing import List, Optional
from modelos.usuario import Usuario
from modelos.excepciones import (
    UsuarioNoEncontradoError,
    DuplicadoError,
    ValidacionError,
    CredencialesInvalidasError
)


class UsuarioController:
    """Controlador para gestionar operaciones de usuarios"""

    def __init__(self, conexion: sqlite3.Connection):
        self.conn = conexion

    def agregar(self, usuario: Usuario) -> Usuario:
        """Agrega un nuevo usuario a la base de datos"""
        if not usuario.username:
            raise ValidacionError("username", "El nombre de usuario es obligatorio")
        if not usuario.password:
            raise ValidacionError("password", "La contraseña es obligatoria")
        if usuario.rol not in Usuario.ROLES_VALIDOS:
            raise ValidacionError("rol", f"El rol debe ser uno de: {Usuario.ROLES_VALIDOS}")

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO usuarios (username, password, rol)
                VALUES (?, ?, ?)
            """, (
                usuario.username,
                usuario.password,
                usuario.rol
            ))
            self.conn.commit()

            # Obtener el ID generado
            usuario.id = cursor.lastrowid
            return usuario

        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise DuplicadoError("Usuario", usuario.username)

    def buscar(self, usuario_id: int) -> Usuario:
        """Busca un usuario por su ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise UsuarioNoEncontradoError(str(usuario_id))

        return Usuario.from_row(resultado)

    def buscar_por_username(self, username: str) -> Usuario:
        """Busca un usuario por su nombre de usuario"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        resultado = cursor.fetchone()

        if not resultado:
            raise UsuarioNoEncontradoError(username)

        return Usuario.from_row(resultado)

    def autenticar(self, username: str, password: str) -> Usuario:
        """Autentica un usuario con username y password"""
        try:
            usuario = self.buscar_por_username(username)
            if usuario.verificar_password(password):
                return usuario
            else:
                raise CredencialesInvalidasError()
        except UsuarioNoEncontradoError:
            raise CredencialesInvalidasError()

    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza los datos de un usuario existente"""
        if not usuario.id:
            raise ValidacionError("id", "El ID es obligatorio para actualizar")

        self.buscar(usuario.id)

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET username = ?, password = ?, rol = ?
            WHERE id = ?
        """, (
            usuario.username,
            usuario.password,
            usuario.rol,
            usuario.id
        ))
        self.conn.commit()
        return usuario

    def cambiar_password(self, usuario_id: int, nuevo_password: str) -> Usuario:
        """Cambia la contraseña de un usuario"""
        usuario = self.buscar(usuario_id)
        usuario.password = nuevo_password
        return self.actualizar(usuario)

    def eliminar(self, usuario_id: int) -> bool:
        """Elimina un usuario de la base de datos"""
        self.buscar(usuario_id)

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        self.conn.commit()
        return True

    def listar(self) -> List[Usuario]:
        """Lista todos los usuarios"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios ORDER BY username")
        resultados = cursor.fetchall()
        return [Usuario.from_row(row) for row in resultados]

    def listar_por_rol(self, rol: str) -> List[Usuario]:
        """Lista usuarios por rol"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE rol = ? ORDER BY username",
            (rol,)
        )
        resultados = cursor.fetchall()
        return [Usuario.from_row(row) for row in resultados]

    def contar(self) -> int:
        """Retorna el número total de usuarios"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        return cursor.fetchone()[0]

    def existe_username(self, username: str) -> bool:
        """Verifica si un username ya existe"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()[0] > 0
