"""
Módulo modelos - Clases de dominio del sistema
"""
from .excepciones import (
    SistemaVentasError,
    ClienteNoEncontradoError,
    ProductoNoEncontradoError,
    ProveedorNoEncontradoError,
    VentaNoEncontradaError,
    UsuarioNoEncontradoError,
    StockInsuficienteError,
    DuplicadoError,
    ValidacionError
)
from .cliente import Cliente
from .producto import Producto
from .proveedor import Proveedor
from .venta import Venta
from .usuario import Usuario
