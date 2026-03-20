"""
Módulo de conexión a base de datos SQLite
Gestiona la conexión y creación de tablas del sistema de ventas
"""
import sqlite3
import os


class DatabaseConnection:
    """Clase singleton para gestionar la conexión a SQLite"""

    _instance = None
    _connection = None

    def __new__(cls, db_path: str = "sistema_ventas.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db_path = db_path
        return cls._instance

    def __init__(self, db_path: str = "sistema_ventas.db"):
        self._db_path = db_path

    def conectar(self) -> sqlite3.Connection:
        """Establece o retorna la conexión existente"""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            # Habilitar llaves foráneas
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_cursor(self) -> sqlite3.Cursor:
        """Obtiene un cursor de la conexión"""
        return self.conectar().cursor()

    def commit(self):
        """Confirma los cambios en la base de datos"""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Revierte los cambios no confirmados"""
        if self._connection:
            self._connection.rollback()


def crear_conexion(db_path: str = "sistema_ventas.db") -> sqlite3.Connection:
    """Función auxiliar para crear una conexión simple"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_tablas(conn: sqlite3.Connection):
    """Crea todas las tablas del sistema si no existen"""
    cursor = conn.cursor()

    # Tabla de usuarios (admin/cajero)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('admin', 'cajero'))
        )
    """)

    # Tabla de proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            direccion TEXT
        )
    """)

    # Tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            correo TEXT,
            telefono TEXT,
            direccion TEXT
        )
    """)

    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT,
            stock INTEGER NOT NULL DEFAULT 0,
            descripcion TEXT,
            stock_minimo INTEGER DEFAULT 5,
            proveedor_id TEXT,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)

    # Tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            producto_id TEXT NOT NULL,
            cantidad REAL NOT NULL,
            descuento REAL DEFAULT 0,
            fecha TEXT NOT NULL,
            estado TEXT DEFAULT 'activa' CHECK(estado IN ('activa', 'devuelta')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.commit()
    print("[OK] Tablas creadas correctamente")


def eliminar_tablas(conn: sqlite3.Connection):
    """Elimina todas las tablas (útil para reiniciar la BD)"""
    cursor = conn.cursor()

    # Orden importante por las llaves foráneas
    tablas = ['ventas', 'productos', 'clientes', 'proveedores', 'usuarios']

    for tabla in tablas:
        cursor.execute(f"DROP TABLE IF EXISTS {tabla}")

    conn.commit()
    print("[OK] Tablas eliminadas")


def verificar_tablas(conn: sqlite3.Connection) -> dict:
    """Verifica que todas las tablas existan y retorna conteo de registros"""
    cursor = conn.cursor()
    tablas = ['usuarios', 'proveedores', 'clientes', 'productos', 'ventas']
    resultado = {}

    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            resultado[tabla] = count
        except sqlite3.OperationalError:
            resultado[tabla] = -1  # Tabla no existe

    return resultado
