"""
Modelo Cliente - Representa un cliente del sistema de ventas
"""
from typing import List, Optional


class Cliente:
    """Clase que representa un cliente"""

    def __init__(
        self,
        id: str,
        nombre: str,
        correo: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        historial_compras: Optional[List] = None
    ):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.direccion = direccion
        self.historial_compras = historial_compras if historial_compras else []

    def __str__(self) -> str:
        return f"Cliente({self.id}, {self.nombre})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'correo': self.correo,
            'telefono': self.telefono,
            'direccion': self.direccion
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Cliente':
        """Crea un cliente desde un diccionario"""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            correo=data.get('correo'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            historial_compras=data.get('historial_compras', [])
        )

    @classmethod
    def from_row(cls, row) -> 'Cliente':
        """Crea un cliente desde una fila de SQLite"""
        return cls(
            id=row['id'],
            nombre=row['nombre'],
            correo=row['correo'],
            telefono=row['telefono'],
            direccion=row['direccion']
        )

    def agregar_compra(self, venta_id: str):
        """Agrega una venta al historial de compras"""
        if venta_id not in self.historial_compras:
            self.historial_compras.append(venta_id)

    def total_compras(self) -> int:
        """Retorna el número total de compras del cliente"""
        return len(self.historial_compras)
