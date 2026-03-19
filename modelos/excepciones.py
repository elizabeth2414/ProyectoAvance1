"""
Excepciones personalizadas del Sistema de Gestión de Ventas
"""


class SistemaVentasError(Exception):
    """Excepción base del sistema de ventas"""

    def __init__(self, mensaje: str = "Error en el sistema de ventas"):
        self.mensaje = mensaje
        super().__init__(self.mensaje)


class ClienteNoEncontradoError(SistemaVentasError):
    """Se lanza cuando no se encuentra un cliente"""

    def __init__(self, cliente_id: str = None):
        mensaje = f"Cliente no encontrado: {cliente_id}" if cliente_id else "Cliente no encontrado"
        super().__init__(mensaje)


class ProductoNoEncontradoError(SistemaVentasError):
    """Se lanza cuando no se encuentra un producto"""

    def __init__(self, producto_id: str = None):
        mensaje = f"Producto no encontrado: {producto_id}" if producto_id else "Producto no encontrado"
        super().__init__(mensaje)


class ProveedorNoEncontradoError(SistemaVentasError):
    """Se lanza cuando no se encuentra un proveedor"""

    def __init__(self, proveedor_id: str = None):
        mensaje = f"Proveedor no encontrado: {proveedor_id}" if proveedor_id else "Proveedor no encontrado"
        super().__init__(mensaje)


class VentaNoEncontradaError(SistemaVentasError):
    """Se lanza cuando no se encuentra una venta"""

    def __init__(self, venta_id: str = None):
        mensaje = f"Venta no encontrada: {venta_id}" if venta_id else "Venta no encontrada"
        super().__init__(mensaje)


class UsuarioNoEncontradoError(SistemaVentasError):
    """Se lanza cuando no se encuentra un usuario"""

    def __init__(self, usuario_id: str = None):
        mensaje = f"Usuario no encontrado: {usuario_id}" if usuario_id else "Usuario no encontrado"
        super().__init__(mensaje)


class StockInsuficienteError(SistemaVentasError):
    """Se lanza cuando no hay suficiente stock para una venta"""

    def __init__(self, producto_id: str = None, stock_actual: int = 0, cantidad_solicitada: int = 0):
        mensaje = f"Stock insuficiente para producto {producto_id}. "
        mensaje += f"Stock actual: {stock_actual}, Cantidad solicitada: {cantidad_solicitada}"
        super().__init__(mensaje)
        self.producto_id = producto_id
        self.stock_actual = stock_actual
        self.cantidad_solicitada = cantidad_solicitada


class DuplicadoError(SistemaVentasError):
    """Se lanza cuando se intenta crear un registro duplicado"""

    def __init__(self, entidad: str = "Registro", identificador: str = None):
        mensaje = f"{entidad} duplicado"
        if identificador:
            mensaje += f": {identificador}"
        super().__init__(mensaje)


class ValidacionError(SistemaVentasError):
    """Se lanza cuando hay errores de validación de datos"""

    def __init__(self, campo: str = None, mensaje: str = "Error de validación"):
        if campo:
            mensaje = f"Error de validación en {campo}: {mensaje}"
        super().__init__(mensaje)
        self.campo = campo


class CredencialesInvalidasError(SistemaVentasError):
    """Se lanza cuando las credenciales de login son incorrectas"""

    def __init__(self):
        super().__init__("Usuario o contraseña incorrectos")


class PermisoInsuficienteError(SistemaVentasError):
    """Se lanza cuando el usuario no tiene permisos para una acción"""

    def __init__(self, accion: str = None):
        mensaje = "Permisos insuficientes"
        if accion:
            mensaje += f" para: {accion}"
        super().__init__(mensaje)
