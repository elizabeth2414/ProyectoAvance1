"""
Sistema de Gestion de Ventas
============================
Archivo principal con interfaz grafica PyQt6

Arquitectura: MVC (Modelo-Vista-Controlador)
Base de datos: SQLite
UI: PyQt6
"""
import os
import sys

# Evita advertencias de Qt por fuentes faltantes en algunos entornos.
os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

from PyQt6.QtWidgets import QApplication

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.conexion import crear_conexion, crear_tablas, verificar_tablas
from modelos.cliente import Cliente
from modelos.producto import Producto
from modelos.proveedor import Proveedor
from modelos.venta import Venta
from modelos.usuario import Usuario
from controladores.cliente_controller import ClienteController
from controladores.producto_controller import ProductoController
from controladores.proveedor_controller import ProveedorController
from controladores.venta_controller import VentaController
from controladores.usuario_controller import UsuarioController


def cargar_datos_prueba(conn):
    """Carga datos de prueba en la base de datos"""

    # Inicializar controladores
    usuario_ctrl = UsuarioController(conn)
    proveedor_ctrl = ProveedorController(conn)
    cliente_ctrl = ClienteController(conn)
    producto_ctrl = ProductoController(conn)
    venta_ctrl = VentaController(conn)

    print("\n" + "=" * 60)
    print("CARGANDO DATOS DE PRUEBA")
    print("=" * 60)

    # ==================== USUARIOS ====================
    print("\n[1/5] Creando usuarios...")
    usuarios_data = [
        Usuario(None, "admin", "admin123", "admin"),
        Usuario(None, "cajero", "cajero123", "cajero")
    ]

    for usuario in usuarios_data:
        try:
            usuario_ctrl.agregar(usuario)
            print(f"   + Usuario creado: {usuario.username} ({usuario.rol})")
        except Exception as e:
            print(f"   - Usuario {usuario.username} ya existe")

    # ==================== PROVEEDORES ====================
    print("\n[2/5] Creando proveedores...")
    proveedores_data = [
        Proveedor(
            "PRV-001",
            "Distribuidora El Mayorista",
            "555-1234",
            "mayorista@email.com",
            "Av. Industrial 123"
        ),
        Proveedor(
            "PRV-002",
            "Importadora Global S.A.",
            "555-5678",
            "global@email.com",
            "Calle Comercio 456"
        )
    ]

    for proveedor in proveedores_data:
        try:
            proveedor_ctrl.agregar(proveedor)
            print(f"   + Proveedor creado: {proveedor.nombre}")
        except Exception as e:
            print(f"   - Proveedor {proveedor.id} ya existe")

    # ==================== CLIENTES ====================
    print("\n[3/5] Creando clientes...")
    clientes_data = [
        Cliente(
            "CLI-001",
            "Juan Perez Garcia",
            "juan.perez@email.com",
            "555-0001",
            "Calle Principal 100"
        ),
        Cliente(
            "CLI-002",
            "Maria Lopez Sanchez",
            "maria.lopez@email.com",
            "555-0002",
            "Av. Central 200"
        ),
        Cliente(
            "CLI-003",
            "Carlos Rodriguez Martinez",
            "carlos.rod@email.com",
            "555-0003",
            "Jr. Las Flores 300"
        ),
        Cliente(
            "CLI-004",
            "Ana Torres Vargas",
            "ana.torres@email.com",
            "555-0004",
            "Psje. Los Alamos 400"
        ),
        Cliente(
            "CLI-005",
            "Pedro Mendoza Rios",
            "pedro.mendoza@email.com",
            "555-0005",
            "Calle Nueva 500"
        ),
        Cliente(
            "CLI-006",
            "Sofia Morales Castro",
            "sofia.morales@email.com",
            "555-0006",
            "Av. Libertad 600"
        ),
        Cliente(
            "CLI-007",
            "Roberto Gutierrez Flores",
            "roberto.gut@email.com",
            "555-0007",
            "Calle Espana 700"
        ),
        Cliente(
            "CLI-008",
            "Claudia Romero Silva",
            "claudia.romero@email.com",
            "555-0008",
            "Jr. America 800"
        ),
        Cliente(
            "CLI-009",
            "Francisco Diaz Herrera",
            "francisco.diaz@email.com",
            "555-0009",
            "Psje. San Martin 900"
        ),
        Cliente(
            "CLI-010",
            "Patricia Vega Nunez",
            "patricia.vega@email.com",
            "555-0010",
            "Calle Matriz 1000"
        )
    ]

    for cliente in clientes_data:
        try:
            cliente_ctrl.agregar(cliente)
            print(f"   + Cliente creado: {cliente.nombre}")
        except Exception as e:
            print(f"   - Cliente {cliente.id} ya existe")

    # ==================== PRODUCTOS ====================
    print("\n[4/5] Creando productos...")
    productos_data = [
        Producto(
            "PRD-001",
            "Laptop HP Pavilion 15",
            2500.00,
            "Electronicos",
            50,
            "Laptop 15.6 pulgadas, 8GB RAM, 512GB SSD",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-002",
            "Mouse Inalambrico Logitech",
            45.00,
            "Accesorios",
            30,
            "Mouse ergonomico inalambrico",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-003",
            "Teclado Mecanico RGB",
            120.00,
            "Accesorios",
            25,
            "Teclado mecanico con iluminacion RGB",
            5,
            "PRV-002"
        ),
        Producto(
            "PRD-004",
            "Monitor Samsung 24 pulgadas",
            350.00,
            "Electronicos",
            40,
            "Monitor Full HD IPS",
            5,
            "PRV-002"
        ),
        Producto(
            "PRD-005",
            "Audifonos Bluetooth Sony",
            180.00,
            "Audio",
            20,
            "Audifonos con cancelacion de ruido",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-006",
            "Webcam Logitech 4K",
            150.00,
            "Accesorios",
            15,
            "Webcam 4K para videoconferencias",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-007",
            "SSD Samsung 1TB",
            280.00,
            "Electronicos",
            35,
            "Unidad SSD NVMe 1TB",
            5,
            "PRV-002"
        ),
        Producto(
            "PRD-008",
            "RAM DDR4 16GB",
            320.00,
            "Electronicos",
            22,
            "Memoria RAM DDR4 16GB",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-009",
            "Cables HDMI 2.0",
            25.00,
            "Accesorios",
            100,
            "Cable HDMI 2.0 alta velocidad",
            10,
            "PRV-002"
        ),
        Producto(
            "PRD-010",
            "Hub USB-C 7 puertos",
            85.00,
            "Accesorios",
            18,
            "Hub USB-C con multiples puertos",
            5,
            "PRV-001"
        ),
        Producto(
            "PRD-011",
            "Impresora HP LaserJet",
            450.00,
            "Electronicos",
            8,
            "Impresora laser monocromatica",
            3,
            "PRV-002"
        ),
        Producto(
            "PRD-012",
            "Escaner Epson 1200dpi",
            200.00,
            "Electronicos",
            12,
            "Escaner de documentos",
            3,
            "PRV-001"
        ),
        Producto(
            "PRD-013",
            "Router TP-Link WiFi 6",
            120.00,
            "Redes",
            14,
            "Router WiFi 6 de alta velocidad",
            5,
            "PRV-002"
        ),
        Producto(
            "PRD-014",
            "Funda para Laptop 15.6",
            35.00,
            "Accesorios",
            45,
            "Funda protectora para laptop",
            10,
            "PRV-001"
        ),
        Producto(
            "PRD-015",
            "Mochila para Laptop",
            65.00,
            "Accesorios",
            28,
            "Mochila ergonomica con compartimientos",
            5,
            "PRV-002"
        ),
        Producto(
            "PRD-016",
            "Power Bank 20000mAh",
            55.00,
            "Accesorios",
            36,
            "Bateria externa 20000mAh",
            10,
            "PRV-001"
        ),
        Producto(
            "PRD-017",
            "Adaptador HDMI-VGA",
            30.00,
            "Accesorios",
            50,
            "Convertidor HDMI a VGA",
            10,
            "PRV-002"
        ),
        Producto(
            "PRD-018",
            "Cooler CPU Noctua",
            95.00,
            "Electronicos",
            11,
            "Cooler para procesador",
            3,
            "PRV-001"
        ),
        Producto(
            "PRD-019",
            "Pasta Termica Arctic",
            15.00,
            "Accesorios",
            60,
            "Pasta termica para procesadores",
            20,
            "PRV-002"
        ),
        Producto(
            "PRD-020",
            "Limpiador Electronico",
            20.00,
            "Mantenimiento",
            40,
            "Spray limpiador para equipos",
            10,
            "PRV-001"
        )
    ]

    for producto in productos_data:
        try:
            producto_ctrl.agregar(producto)
            estado = "CRITICO" if producto.es_stock_critico() else "OK"
            print(f"   + Producto creado: {producto.nombre} (Stock: {producto.stock} [{estado}])")
        except Exception as e:
            print(f"   - Producto {producto.id} ya existe")

    # ==================== VENTAS ====================
    print("\n[5/5] Creando ventas de prueba...")
    ventas_data = []

    # 5 ventas por cada cliente (10 clientes = 50 ventas)
    # Distribuidas del 01 enero al 20 marzo 2026
    ventas_config = [
        # Cliente CLI-001 (enero)
        ("VEN-001", "CLI-001", "PRD-001", 1, 0, "2026-01-05 10:30:00"),
        ("VEN-002", "CLI-001", "PRD-002", 3, 5, "2026-01-12 14:20:00"),
        ("VEN-003", "CLI-001", "PRD-004", 1, 10, "2026-01-19 09:15:00"),
        ("VEN-004", "CLI-001", "PRD-005", 2, 0, "2026-01-26 16:45:00"),
        ("VEN-005", "CLI-001", "PRD-003", 1, 15, "2026-02-02 11:30:00"),
        # Cliente CLI-002 (enero-febrero)
        ("VEN-006", "CLI-002", "PRD-002", 2, 10, "2026-01-08 13:00:00"),
        ("VEN-007", "CLI-002", "PRD-006", 1, 0, "2026-01-15 10:45:00"),
        ("VEN-008", "CLI-002", "PRD-007", 1, 5, "2026-01-22 15:20:00"),
        ("VEN-009", "CLI-002", "PRD-009", 5, 20, "2026-01-29 12:10:00"),
        ("VEN-010", "CLI-002", "PRD-010", 1, 0, "2026-02-05 08:55:00"),
        # Cliente CLI-003 (febrero)
        ("VEN-011", "CLI-003", "PRD-004", 1, 5, "2026-02-02 14:30:00"),
        ("VEN-012", "CLI-003", "PRD-011", 1, 0, "2026-02-09 09:20:00"),
        ("VEN-013", "CLI-003", "PRD-012", 1, 10, "2026-02-16 16:15:00"),
        ("VEN-014", "CLI-003", "PRD-014", 2, 0, "2026-02-23 13:40:00"),
        ("VEN-015", "CLI-003", "PRD-015", 1, 15, "2026-03-02 10:25:00"),
        # Cliente CLI-004 (febrero-marzo)
        ("VEN-016", "CLI-004", "PRD-001", 1, 0, "2026-02-04 11:15:00"),
        ("VEN-017", "CLI-004", "PRD-013", 1, 5, "2026-02-11 14:50:00"),
        ("VEN-018", "CLI-004", "PRD-016", 2, 10, "2026-02-18 10:30:00"),
        ("VEN-019", "CLI-004", "PRD-017", 3, 0, "2026-02-25 15:05:00"),
        ("VEN-020", "CLI-004", "PRD-018", 1, 20, "2026-03-05 12:45:00"),
        # Cliente CLI-005 (febrero)
        ("VEN-021", "CLI-005", "PRD-005", 1, 10, "2026-02-07 15:40:00"),
        ("VEN-022", "CLI-005", "PRD-008", 1, 0, "2026-02-14 11:25:00"),
        ("VEN-023", "CLI-005", "PRD-009", 4, 5, "2026-02-21 13:50:00"),
        ("VEN-024", "CLI-005", "PRD-019", 2, 0, "2026-02-28 09:30:00"),
        ("VEN-025", "CLI-005", "PRD-020", 1, 15, "2026-03-07 14:20:00"),
        # Cliente CLI-006 (febrero-marzo)
        ("VEN-026", "CLI-006", "PRD-003", 1, 5, "2026-02-06 12:00:00"),
        ("VEN-027", "CLI-006", "PRD-006", 1, 0, "2026-02-13 15:35:00"),
        ("VEN-028", "CLI-006", "PRD-010", 2, 10, "2026-02-20 11:10:00"),
        ("VEN-029", "CLI-006", "PRD-011", 1, 0, "2026-03-01 16:55:00"),
        ("VEN-030", "CLI-006", "PRD-014", 3, 20, "2026-03-08 09:40:00"),
        # Cliente CLI-007 (febrero-marzo)
        ("VEN-031", "CLI-007", "PRD-002", 1, 0, "2026-02-10 16:20:00"),
        ("VEN-032", "CLI-007", "PRD-007", 1, 5, "2026-02-17 12:45:00"),
        ("VEN-033", "CLI-007", "PRD-012", 1, 10, "2026-02-24 14:15:00"),
        ("VEN-034", "CLI-007", "PRD-016", 1, 0, "2026-03-03 10:50:00"),
        ("VEN-035", "CLI-007", "PRD-018", 1, 15, "2026-03-10 15:30:00"),
        # Cliente CLI-008 (marzo)
        ("VEN-036", "CLI-008", "PRD-004", 1, 5, "2026-03-01 10:05:00"),
        ("VEN-037", "CLI-008", "PRD-009", 2, 0, "2026-03-04 13:35:00"),
        ("VEN-038", "CLI-008", "PRD-013", 1, 10, "2026-03-08 16:50:00"),
        ("VEN-039", "CLI-008", "PRD-015", 2, 0, "2026-03-11 11:20:00"),
        ("VEN-040", "CLI-008", "PRD-019", 1, 20, "2026-03-14 13:10:00"),
        # Cliente CLI-009 (marzo)
        ("VEN-041", "CLI-009", "PRD-001", 1, 0, "2026-03-02 14:50:00"),
        ("VEN-042", "CLI-009", "PRD-005", 1, 5, "2026-03-06 10:15:00"),
        ("VEN-043", "CLI-009", "PRD-008", 1, 10, "2026-03-09 15:40:00"),
        ("VEN-044", "CLI-009", "PRD-017", 2, 0, "2026-03-13 12:25:00"),
        ("VEN-045", "CLI-009", "PRD-020", 3, 15, "2026-03-16 10:50:00"),
        # Cliente CLI-010 (marzo)
        ("VEN-046", "CLI-010", "PRD-003", 1, 5, "2026-03-03 11:40:00"),
        ("VEN-047", "CLI-010", "PRD-006", 1, 0, "2026-03-07 16:20:00"),
        ("VEN-048", "CLI-010", "PRD-010", 1, 10, "2026-03-10 12:55:00"),
        ("VEN-049", "CLI-010", "PRD-012", 1, 0, "2026-03-15 14:35:00"),
        ("VEN-050", "CLI-010", "PRD-014", 2, 20, "2026-03-20 11:15:00"),
    ]

    for ven_id, cli_id, prod_id, cant, desc, fecha in ventas_config:
        ventas_data.append(Venta(
            ven_id,
            cli_id,
            prod_id,
            cant,
            desc,
            fecha,
            "activa"
        ))

    for venta in ventas_data:
        try:
            venta_ctrl.agregar(venta, reducir_stock=False)  # No reducir stock (datos de prueba)
            total = venta_ctrl.calcular_total_venta(venta.id)
            print(f"   + Venta creada: {venta.id} - Total: ${total:.2f}")
        except Exception as e:
            print(f"   - Venta {venta.id} ya existe o error: {e}")


def mostrar_resumen(conn):
    """Muestra un resumen del estado de la base de datos"""

    print("\n" + "=" * 60)
    print("RESUMEN DEL SISTEMA")
    print("=" * 60)

    # Verificar tablas
    tablas = verificar_tablas(conn)
    print("\nRegistros por tabla:")
    for tabla, count in tablas.items():
        estado = "OK" if count >= 0 else "ERROR"
        print(f"   {tabla}: {count} registros [{estado}]")

    # Resumen de productos con stock critico
    producto_ctrl = ProductoController(conn)
    productos_criticos = producto_ctrl.listar_stock_critico()

    if productos_criticos:
        print(f"\n[!] ALERTA: {len(productos_criticos)} producto(s) con stock critico:")
        for prod in productos_criticos:
            print(f"   - {prod.nombre}: {prod.stock} unidades (minimo: {prod.stock_minimo})")

    # Resumen de ventas
    venta_ctrl = VentaController(conn)
    resumen_ventas = venta_ctrl.obtener_resumen_ventas()
    print(f"\nResumen de ventas:")
    print(f"   Total ventas activas: {resumen_ventas['total_ventas']}")
    print(f"   Monto total: ${resumen_ventas['monto_total']:.2f}")
    print(f"   Ventas devueltas: {resumen_ventas['ventas_devueltas']}")


class SistemaVentas:
    """Clase principal que gestiona el flujo de la aplicacion"""

    def __init__(self):
        self.conexion = None
        self.usuario_actual = None
        self.qt_app = None
        self.ventana_login = None
        self.ventana_principal = None

    def inicializar_bd(self):
        """Inicializa la base de datos"""
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sistema_ventas.db"
        )

        self.conexion = crear_conexion(db_path)
        crear_tablas(self.conexion)

        # Verificar si hay datos, si no cargar datos de prueba
        tablas = verificar_tablas(self.conexion)
        if tablas.get('usuarios', 0) == 0:
            print("\nPrimera ejecucion - Cargando datos de prueba...")
            cargar_datos_prueba(self.conexion)
            mostrar_resumen(self.conexion)
        else:
            print("\nBase de datos existente cargada correctamente")
            print(f"   Usuarios: {tablas['usuarios']}")
            print(f"   Clientes: {tablas['clientes']}")
            print(f"   Productos: {tablas['productos']}")
            print(f"   Ventas: {tablas['ventas']}")

    def iniciar(self):
        """Inicia la aplicacion"""
        print("\n" + "=" * 60)
        print("SISTEMA DE GESTION DE VENTAS")
        print("Iniciando aplicacion...")
        print("=" * 60)

        self.qt_app = QApplication(sys.argv)

        # Inicializar base de datos
        self.inicializar_bd()

        # Mostrar login
        self._mostrar_login()
        return self.qt_app.exec()

    def _mostrar_login(self):
        """Muestra la ventana de login"""
        from vistas.login import LoginWindow

        self.ventana_login = LoginWindow(
            self.conexion,
            on_login_success=self._on_login_exitoso
        )
        self.ventana_login.show()

    def _on_login_exitoso(self, usuario):
        """Callback cuando el login es exitoso"""
        print(f"\n[OK] Usuario autenticado: {usuario.username} ({usuario.rol})")
        self.usuario_actual = usuario

        # Ocultar login y mostrar ventana principal
        self.ventana_login.hide()

        self._mostrar_ventana_principal()

    def _mostrar_ventana_principal(self):
        """Muestra la ventana principal"""
        from vistas.app import AppPrincipal

        self.ventana_principal = AppPrincipal(
            self.conexion,
            self.usuario_actual,
            on_logout=self._on_logout
        )
        self.ventana_principal.destroyed.connect(
            lambda: self._cerrar_aplicacion() if self.usuario_actual else None
        )
        self.ventana_principal.show()

    def _on_logout(self):
        """Callback cuando el usuario cierra sesion"""
        print(f"\n[OK] Sesion cerrada: {self.usuario_actual.username}")
        self.usuario_actual = None

        # Destruir ventana principal si existe
        if self.ventana_principal:
            try:
                self.ventana_principal.destroy()
            except:
                pass
            self.ventana_principal = None

        # Volver a mostrar login
        self.ventana_login.show()
        self.ventana_login.limpiar_campos()

    def _cerrar_aplicacion(self):
        """Cierra la aplicacion completamente"""
        print("\n" + "=" * 60)
        print("Cerrando Sistema de Gestion de Ventas...")
        print("=" * 60 + "\n")

        # Cerrar conexion BD
        if self.conexion:
            self.conexion.close()

        # Destruir ventanas
        if self.ventana_principal:
            try:
                self.ventana_principal.close()
            except Exception:
                pass

        if self.ventana_login:
            try:
                self.ventana_login.close()
            except Exception:
                pass
        if self.qt_app:
            self.qt_app.quit()


def main():
    """Funcion principal"""
    app = SistemaVentas()
    return app.iniciar()


if __name__ == "__main__":
    sys.exit(main())
