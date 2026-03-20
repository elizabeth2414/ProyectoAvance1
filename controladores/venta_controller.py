"""
Controlador de Ventas - Gestiona operaciones CRUD con SQLite
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from modelos.venta import Venta
from modelos.excepciones import (
    VentaNoEncontradaError,
    DuplicadoError,
    ValidacionError,
    StockInsuficienteError,
    ClienteNoEncontradoError,
    ProductoNoEncontradoError
)


class VentaController:
    """Controlador para gestionar operaciones de ventas"""

    def __init__(self, conexion: sqlite3.Connection):
        self.conn = conexion

    def _generar_id(self) -> str:
        """Genera un nuevo ID para venta consultando el último ID en BD"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM ventas ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()

        if resultado:
            ultimo_id = resultado['id']
            numero = int(ultimo_id.split('-')[1]) + 1
        else:
            numero = 1

        return f"VEN-{numero:03d}"

    def previsualizar_id(self) -> str:
        """Retorna el próximo ID disponible para mostrar en formularios."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM ventas ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        if resultado:
            numero = int(resultado['id'].split('-')[1]) + 1
        else:
            numero = 1
        return f"VEN-{numero:03d}"

    def _verificar_cliente(self, cliente_id: str):
        """Verifica que el cliente exista"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
        if not cursor.fetchone():
            raise ClienteNoEncontradoError(cliente_id)

    def _verificar_producto(self, producto_id: str) -> dict:
        """Verifica que el producto exista y retorna sus datos"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        if not producto:
            raise ProductoNoEncontradoError(producto_id)
        return producto

    def agregar(self, venta: Venta, reducir_stock: bool = True) -> Venta:
        """Agrega una nueva venta a la base de datos"""
        if venta.cantidad <= 0:
            raise ValidacionError("cantidad", "La cantidad debe ser mayor a 0")

        # Verificar que existan cliente y producto
        self._verificar_cliente(venta.cliente_id)
        producto = self._verificar_producto(venta.producto_id)

        # Verificar stock disponible
        if reducir_stock and producto['stock'] < venta.cantidad:
            raise StockInsuficienteError(
                venta.producto_id,
                producto['stock'],
                int(venta.cantidad)
            )

        if not venta.id:
            venta.id = self._generar_id()

        if not venta.fecha:
            venta.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.conn.cursor()

        try:
            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas
                (id, cliente_id, producto_id, cantidad, descuento, fecha, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                venta.id,
                venta.cliente_id,
                venta.producto_id,
                venta.cantidad,
                venta.descuento,
                venta.fecha,
                venta.estado
            ))

            # Reducir stock del producto
            if reducir_stock:
                cursor.execute("""
                    UPDATE productos SET stock = stock - ? WHERE id = ?
                """, (venta.cantidad, venta.producto_id))

            self.conn.commit()
            return venta

        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise DuplicadoError("Venta", venta.id)

    def buscar(self, venta_id: str) -> Venta:
        """Busca una venta por su ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise VentaNoEncontradaError(venta_id)

        return Venta.from_row(resultado)

    def buscar_por_cliente(self, cliente_id: str) -> List[Venta]:
        """Busca ventas por cliente"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM ventas WHERE cliente_id = ? ORDER BY fecha DESC",
            (cliente_id,)
        )
        resultados = cursor.fetchall()
        return [Venta.from_row(row) for row in resultados]

    def buscar_por_fecha(self, fecha_inicio: str, fecha_fin: str) -> List[Venta]:
        """Busca ventas en un rango de fechas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM ventas
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """, (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        return [Venta.from_row(row) for row in resultados]

    def actualizar(self, venta: Venta) -> Venta:
        """Actualiza los datos de una venta existente"""
        if not venta.id:
            raise ValidacionError("id", "El ID es obligatorio para actualizar")

        self.buscar(venta.id)

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE ventas
            SET cliente_id = ?, producto_id = ?, cantidad = ?,
                descuento = ?, fecha = ?, estado = ?
            WHERE id = ?
        """, (
            venta.cliente_id,
            venta.producto_id,
            venta.cantidad,
            venta.descuento,
            venta.fecha,
            venta.estado,
            venta.id
        ))
        self.conn.commit()
        return venta

    def eliminar(self, venta_id: str) -> bool:
        """Elimina una venta de la base de datos"""
        self.buscar(venta_id)

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        self.conn.commit()
        return True

    def devolver(self, venta_id: str) -> Venta:
        """Marca una venta como devuelta y restaura el stock"""
        venta = self.buscar(venta_id)

        if venta.es_devuelta():
            raise ValidacionError("estado", "La venta ya fue devuelta")

        cursor = self.conn.cursor()

        # Restaurar stock
        cursor.execute("""
            UPDATE productos SET stock = stock + ? WHERE id = ?
        """, (venta.cantidad, venta.producto_id))

        # Marcar como devuelta
        venta.estado = 'devuelta'
        cursor.execute("""
            UPDATE ventas SET estado = 'devuelta' WHERE id = ?
        """, (venta_id,))

        self.conn.commit()
        return venta

    def listar(self) -> List[Venta]:
        """Lista todas las ventas"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ventas ORDER BY fecha DESC")
        resultados = cursor.fetchall()
        return [Venta.from_row(row) for row in resultados]

    def listar_activas(self) -> List[Venta]:
        """Lista solo las ventas activas"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM ventas WHERE estado = 'activa' ORDER BY fecha DESC"
        )
        resultados = cursor.fetchall()
        return [Venta.from_row(row) for row in resultados]

    def contar(self) -> int:
        """Retorna el número total de ventas"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ventas")
        return cursor.fetchone()[0]

    def calcular_total_venta(self, venta_id: str) -> float:
        """Calcula el total de una venta específica"""
        venta = self.buscar(venta_id)
        producto = self._verificar_producto(venta.producto_id)

        subtotal = producto['precio'] * venta.cantidad
        descuento = subtotal * (venta.descuento / 100)
        return subtotal - descuento

    def obtener_resumen_ventas(self) -> dict:
        """Obtiene un resumen general de ventas"""
        cursor = self.conn.cursor()

        # Total de ventas
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE estado = 'activa'")
        total_ventas = cursor.fetchone()[0]

        # Monto total
        cursor.execute("""
            SELECT SUM(p.precio * v.cantidad * (1 - v.descuento/100))
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado = 'activa'
        """)
        monto_total = cursor.fetchone()[0] or 0

        # Ventas devueltas
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE estado = 'devuelta'")
        ventas_devueltas = cursor.fetchone()[0]

        return {
            'total_ventas': total_ventas,
            'monto_total': monto_total,
            'ventas_devueltas': ventas_devueltas
        }

    def generar_datos_factura(self, venta_id: str) -> dict:
        """Genera todos los datos necesarios para la factura PDF"""
        cursor = self.conn.cursor()

        # Obtener datos completos con JOIN
        cursor.execute("""
            SELECT
                v.id as venta_id,
                v.cantidad,
                v.descuento,
                v.fecha,
                v.estado,
                c.id as cliente_id,
                c.nombre as cliente_nombre,
                c.correo as cliente_correo,
                c.telefono as cliente_telefono,
                c.direccion as cliente_direccion,
                p.id as producto_id,
                p.nombre as producto_nombre,
                p.precio as producto_precio,
                p.categoria as producto_categoria
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN productos p ON v.producto_id = p.id
            WHERE v.id = ?
        """, (venta_id,))

        resultado = cursor.fetchone()
        if not resultado:
            raise VentaNoEncontradaError(venta_id)

        # Calcular totales
        subtotal = resultado['producto_precio'] * resultado['cantidad']
        descuento_monto = subtotal * (resultado['descuento'] / 100)
        total = subtotal - descuento_monto

        return {
            'venta_id': resultado['venta_id'],
            'fecha': resultado['fecha'],
            'estado': resultado['estado'],
            'cliente': {
                'id': resultado['cliente_id'],
                'nombre': resultado['cliente_nombre'],
                'correo': resultado['cliente_correo'],
                'telefono': resultado['cliente_telefono'],
                'direccion': resultado['cliente_direccion']
            },
            'producto': {
                'id': resultado['producto_id'],
                'nombre': resultado['producto_nombre'],
                'precio': resultado['producto_precio'],
                'categoria': resultado['producto_categoria']
            },
            'cantidad': resultado['cantidad'],
            'descuento_porcentaje': resultado['descuento'],
            'subtotal': subtotal,
            'descuento_monto': descuento_monto,
            'total': total
        }

    def ventas_por_dia(self, fecha_inicio: str, fecha_fin: str) -> list:
        """Obtiene ventas agrupadas por dia en un rango de fechas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                DATE(v.fecha) as dia,
                SUM(p.precio * v.cantidad * (1 - v.descuento/100)) as total
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado = 'activa'
              AND DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY DATE(v.fecha)
            ORDER BY dia
        """, (fecha_inicio, fecha_fin))

        return [(row['dia'], row['total'] or 0) for row in cursor.fetchall()]

    def ventas_por_mes(self, anio: int) -> list:
        """Obtiene ventas agrupadas por mes de un anio especifico"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                strftime('%m', v.fecha) as mes,
                SUM(p.precio * v.cantidad * (1 - v.descuento/100)) as total
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado = 'activa'
              AND strftime('%Y', v.fecha) = ?
            GROUP BY strftime('%m', v.fecha)
            ORDER BY mes
        """, (str(anio),))

        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        resultados = {row['mes']: row['total'] or 0 for row in cursor.fetchall()}

        return [(meses[i], resultados.get(f'{i+1:02d}', 0)) for i in range(12)]

    def top_productos(self, limite: int = 5) -> list:
        """Obtiene los productos mas vendidos"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                p.nombre,
                SUM(v.cantidad) as total_vendido
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado = 'activa'
            GROUP BY v.producto_id
            ORDER BY total_vendido DESC
            LIMIT ?
        """, (limite,))

        return [(row['nombre'], row['total_vendido'] or 0) for row in cursor.fetchall()]

    def ventas_por_categoria(self) -> list:
        """Obtiene ventas agrupadas por categoria de producto"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(p.categoria, 'Sin Categoria') as categoria,
                SUM(p.precio * v.cantidad * (1 - v.descuento/100)) as total
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE v.estado = 'activa'
            GROUP BY p.categoria
            ORDER BY total DESC
        """)

        return [(row['categoria'], row['total'] or 0) for row in cursor.fetchall()]
