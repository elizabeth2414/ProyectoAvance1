"""
Modelo Usuario - Representa un usuario del sistema (admin/cajero)
"""
from typing import Optional


class Usuario:
    """Clase que representa un usuario del sistema"""

    ROLES_VALIDOS = ('admin', 'cajero')

    def __init__(
        self,
        id: Optional[int],
        username: str,
        password: str,
        rol: str
    ):
        self.id = id
        self.username = username
        self.password = password
        self.rol = rol if rol in self.ROLES_VALIDOS else 'cajero'

    def __str__(self) -> str:
        return f"Usuario({self.id}, {self.username}, {self.rol})"

    def __repr__(self) -> str:
        return self.__str__()

    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == 'admin'

    def es_cajero(self) -> bool:
        """Verifica si el usuario es cajero"""
        return self.rol == 'cajero'

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return self.password == password

    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario (sin password)"""
        return {
            'id': self.id,
            'username': self.username,
            'rol': self.rol
        }

    def to_dict_completo(self) -> dict:
        """Convierte el usuario a diccionario (con password)"""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'rol': self.rol
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Crea un usuario desde un diccionario"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password=data.get('password', ''),
            rol=data.get('rol', 'cajero')
        )

    @classmethod
    def from_row(cls, row) -> 'Usuario':
        """Crea un usuario desde una fila de SQLite"""
        return cls(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            rol=row['rol']
        )
