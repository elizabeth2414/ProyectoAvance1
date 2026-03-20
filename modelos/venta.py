"""
Modelo Venta - Representa una transacción de venta
"""
from typing import Optional, Union
from datetime import datetime
from .producto import Producto


class Venta:
    """Clase que representa una venta"""

    def __init__(
        self,
        id: str,
        cliente: Union[str, object],  # Puede ser cliente_id o objeto Cliente
        producto: Union[str, Producto],  # Puede ser producto_id o objeto Producto
        cantidad: float,
        descuento: float = 0.0,
        fecha: Optional[str] = None,
        estado: str = 'activa'
    ):
        self.id = id
        # Guardamos el ID si es string, o el objeto si es un objeto
        self.cliente = cliente
        self.producto = producto
        self.cantidad = cantidad
        self.descuento = descuento
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.estado = estado

    def __str__(self) -> str:
        cliente_id = self.cliente if isinstance(self.cliente, str) else self.cliente.id
        return f"Venta({self.id}, Cliente: {cliente_id}, Total: ${self.calcular_total():.2f})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def cliente_id(self) -> str:
        """Retorna el ID del cliente"""
        if isinstance(self.cliente, str):
            return self.cliente
        return self.cliente.id

    @property
    def producto_id(self) -> str:
        """Retorna el ID del producto"""
        if isinstance(self.producto, str):
            return self.producto
        return self.producto.id

    def calcular_total(self) -> float:
        """Calcula el total de la venta aplicando descuento"""
        if isinstance(self.producto, Producto):
            subtotal = self.producto.precio * self.cantidad
        else:
            # Si solo tenemos el ID, no podemos calcular el total real
            return 0.0

        descuento_aplicado = subtotal * (self.descuento / 100)
        return subtotal - descuento_aplicado

    def calcular_total_con_precio(self, precio_unitario: float) -> float:
        """Calcula el total cuando solo tenemos el precio unitario"""
        subtotal = precio_unitario * self.cantidad
        descuento_aplicado = subtotal * (self.descuento / 100)
        return subtotal - descuento_aplicado

    def es_devuelta(self) -> bool:
        """Verifica si la venta fue devuelta"""
        return self.estado == 'devuelta'

    def marcar_devuelta(self):
        """Marca la venta como devuelta"""
        self.estado = 'devuelta'

    def to_dict(self) -> dict:
        """Convierte la venta a diccionario"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'descuento': self.descuento,
            'fecha': self.fecha,
            'estado': self.estado
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Venta':
        """Crea una venta desde un diccionario"""
        return cls(
            id=data.get('id'),
            cliente=data.get('cliente_id'),
            producto=data.get('producto_id'),
            cantidad=data.get('cantidad', 1),
            descuento=data.get('descuento', 0.0),
            fecha=data.get('fecha'),
            estado=data.get('estado', 'activa')
        )

    @classmethod
    def from_row(cls, row) -> 'Venta':
        """Crea una venta desde una fila de SQLite"""
        return cls(
            id=row['id'],
            cliente=row['cliente_id'],
            producto=row['producto_id'],
            cantidad=row['cantidad'],
            descuento=row['descuento'],
            fecha=row['fecha'],
            estado=row['estado']
        )
