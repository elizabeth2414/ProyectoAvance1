"""
Módulo modelos - Clases de dominio del sistema
"""
from .excepciones import (
    SistemaVentasError,
    ProductoNoEncontradoError,
    UsuarioNoEncontradoError,
    StockInsuficienteError,
    DuplicadoError,
    ValidacionError
)
from .producto import Producto
from .usuario import Usuario
