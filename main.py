"""
Sistema de Gestion de Ventas (Versión Simplificada)
====================================================
Archivo principal con interfaz grafica CustomTkinter

Arquitectura: MVC (Modelo-Vista-Controlador)
Base de datos: SQLite
UI: CustomTkinter
"""
import os
import sys
import customtkinter as ctk

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.conexion import crear_conexion, crear_tablas, verificar_tablas
from modelos.usuario import Usuario
from modelos.producto import Producto
from controladores.usuario_controller import UsuarioController
from controladores.producto_controller import ProductoController
from vistas.login import LoginWindow

# Configurar tema oscuro
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def cargar_datos_prueba(conn):
    """Carga datos de prueba basicos en la base de datos"""

    usuario_ctrl = UsuarioController(conn)
    producto_ctrl = ProductoController(conn)

    print("\n" + "=" * 60)
    print("CARGANDO DATOS DE PRUEBA")
    print("=" * 60)

    # ==================== USUARIOS ====================
    print("\n[1/2] Creando usuarios...")
    usuarios_data = [
        Usuario(None, "admin", "admin123", "admin"),
        Usuario(None, "cajero", "cajero123", "cajero")
    ]

    for usuario in usuarios_data:
        try:
            usuario_ctrl.agregar(usuario)
            rol_txt = "Administrador" if usuario.es_admin() else "Cajero"
            print(f"   + Usuario creado: {usuario.username} ({rol_txt})")
        except Exception as e:
            print(f"   - Usuario {usuario.username} ya existe")

    # ==================== PRODUCTOS ====================
    print("\n[2/2] Creando productos de ejemplo...")
    productos_data = [
        Producto(None, "Laptop HP 15.6\"", 1299.99, "Electronica", 10, 2, "Laptop HP con procesador i5", None),
        Producto(None, "Mouse inalambrico", 49.99, "Accesorios", 50, 10, "Mouse inalambrico USB", None),
        Producto(None, "Teclado mecanico", 129.99, "Accesorios", 25, 5, "Teclado mecanico RGB", None),
        Producto(None, "Monitor LG 24\"", 299.99, "Electronica", 8, 2, "Monitor Full HD LG", None),
        Producto(None, "Webcam HD", 89.99, "Accesorios", 15, 5, "Webcam 1080p con microfono", None),
    ]

    for producto in productos_data:
        try:
            producto_ctrl.crear(producto)
            print(f"   + Producto creado: {producto.nombre}")
        except Exception as e:
            print(f"   - Producto {producto.nombre} ya existe")

    print("\n" + "=" * 60)


def main():
    """Punto de entrada principal"""
    
    # Crear conexión a BD
    conn = crear_conexion()
    
    if conn:
        # Crear tablas necesarias
        crear_tablas(conn)
        
        # Cargar datos de prueba
        cargar_datos_prueba(conn)
        
        # Crear y mostrar ventana de login
        login_window = None
        
        def on_login_success(usuario):
            """Se ejecuta cuando el login es exitoso"""
            from vistas.app import AppPrincipal
            
            # Ocultar ventana de login
            if login_window:
                login_window.withdraw()
            
            # Crear ventana principal
            def on_logout_callback():
                """Callback cuando se cierra sesión"""
                app_principal.destroy()
                if login_window:
                    login_window.deiconify()  # Mostrar login nuevamente
            
            app_principal = AppPrincipal(
                conexion=conn,
                usuario=usuario,
                on_logout=on_logout_callback
            )
            
            # Manejar cierre de ventana principal
            def on_app_close():
                app_principal.destroy()
                if login_window:
                    login_window.deiconify()
            
            app_principal.protocol("WM_DELETE_WINDOW", on_app_close)
        
        # Crear y mostrar ventana de login
        login_window = LoginWindow(conn, on_login_success=on_login_success)
        login_window.mainloop()
        
        # Cerrar conexión cuando termine todo
        conn.close()
        
    else:
        print("Error: No se pudo conectar a la base de datos")
        sys.exit(1)


if __name__ == "__main__":
    main()
