"""
Modelo Proveedor - Representa un proveedor de productos
"""
from typing import Optional


class Proveedor:
    """Clase que representa un proveedor"""

    def __init__(
        self,
        id: str,
        nombre: str,
        telefono: Optional[str] = None,
        correo: Optional[str] = None,
        direccion: Optional[str] = None
    ):
        self.id = id
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.direccion = direccion

    def __str__(self) -> str:
        return f"Proveedor({self.id}, {self.nombre})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        """Convierte el proveedor a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'correo': self.correo,
            'direccion': self.direccion
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Proveedor':
        """Crea un proveedor desde un diccionario"""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            direccion=data.get('direccion')
        )

    @classmethod
    def from_row(cls, row) -> 'Proveedor':
        """Crea un proveedor desde una fila de SQLite"""
        return cls(
            id=row['id'],
            nombre=row['nombre'],
            telefono=row['telefono'],
            correo=row['correo'],
            direccion=row['direccion']
        )
