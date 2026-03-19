"""
Modelo Producto - Representa un producto del inventario
"""
from typing import Optional


class Producto:
    """Clase que representa un producto del inventario"""

    def __init__(
        self,
        id: str,
        nombre: str,
        precio: float,
        categoria: Optional[str] = None,
        stock: int = 0,
        descripcion: Optional[str] = None,
        stock_minimo: int = 5,
        proveedor_id: Optional[str] = None
    ):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.stock = stock
        self.descripcion = descripcion
        self.stock_minimo = stock_minimo
        self.proveedor_id = proveedor_id

    def __str__(self) -> str:
        return f"Producto({self.id}, {self.nombre}, ${self.precio:.2f})"

    def __repr__(self) -> str:
        return self.__str__()

    def es_stock_critico(self) -> bool:
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock < self.stock_minimo

    def to_dict(self) -> dict:
        """Convierte el producto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'categoria': self.categoria,
            'stock': self.stock,
            'descripcion': self.descripcion,
            'stock_minimo': self.stock_minimo,
            'proveedor_id': self.proveedor_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Producto':
        """Crea un producto desde un diccionario"""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            precio=data.get('precio', 0.0),
            categoria=data.get('categoria'),
            stock=data.get('stock', 0),
            descripcion=data.get('descripcion'),
            stock_minimo=data.get('stock_minimo', 5),
            proveedor_id=data.get('proveedor_id')
        )

    @classmethod
    def from_row(cls, row) -> 'Producto':
        """Crea un producto desde una fila de SQLite"""
        return cls(
            id=row['id'],
            nombre=row['nombre'],
            precio=row['precio'],
            categoria=row['categoria'],
            stock=row['stock'],
            descripcion=row['descripcion'],
            stock_minimo=row['stock_minimo'],
            proveedor_id=row['proveedor_id']
        )

    def reducir_stock(self, cantidad: int) -> bool:
        """Reduce el stock del producto"""
        if cantidad <= self.stock:
            self.stock -= cantidad
            return True
        return False

    def aumentar_stock(self, cantidad: int):
        """Aumenta el stock del producto"""
        self.stock += cantidad

    def estado_stock(self) -> str:
        """Retorna el estado del stock como texto"""
        if self.stock == 0:
            return "SIN STOCK"
        elif self.es_stock_critico():
            return "STOCK CRITICO"
        else:
            return "DISPONIBLE"
