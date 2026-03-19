"""
Vista Usuarios - CRUD de usuarios (Versión Simplificada)
"""
import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from typing import Optional, List

from .componentes.tabla import TablaPersonalizada
from controladores.usuario_controller import UsuarioController
from modelos.usuario import Usuario


class VistaUsuarios(ctk.CTkFrame):
    """Vista CRUD de usuarios"""

    def __init__(
        self,
        parent,
        conexion: sqlite3.Connection,
        usuario,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.conexion = conexion
        self.usuario = usuario
        self.controller = UsuarioController(conexion)
        self.usuario_seleccionado: Optional[int] = None

        # Solo admin puede acceder
        if not usuario.es_admin():
            self._crear_widgets_restringido()
        else:
            self._crear_widgets()
            self.actualizar()

    def _crear_widgets_restringido(self):
        """Muestra mensaje si no es admin"""
        lbl = ctk.CTkLabel(
            self,
            text="⚠️ Solo administradores pueden acceder a la gestión de usuarios",
            font=ctk.CTkFont(size=14),
            text_color="#ffaa00"
        )
        lbl.pack(expand=True)

    def _crear_widgets(self):
        """Crea los widgets de la vista"""
        # Frame superior
        self.frame_superior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_superior.pack(fill="x", pady=(0, 10))

        # Titulo
        self.lbl_titulo = ctk.CTkLabel(
            self.frame_superior,
            text="Gestion de Usuarios",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_titulo.pack(side="left")

        # Buscador
        self.frame_busqueda = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        self.frame_busqueda.pack(side="right")

        self.entry_buscar = ctk.CTkEntry(
            self.frame_busqueda,
            width=250,
            height=35,
            placeholder_text="Buscar por usuario..."
        )
        self.entry_buscar.pack(side="left", padx=(0, 5))
        self.entry_buscar.bind("<KeyRelease>", self._buscar)

        self.btn_buscar = ctk.CTkButton(
            self.frame_busqueda,
            text="Buscar",
            width=80,
            height=35,
            command=self._buscar
        )
        self.btn_buscar.pack(side="left")

        # Frame botones CRUD
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(fill="x", pady=(0, 10))

        self.btn_agregar = ctk.CTkButton(
            self.frame_botones,
            text="+ Agregar",
            width=100,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            command=self._abrir_formulario_agregar
        )
        self.btn_agregar.pack(side="left", padx=(0, 5))

        self.btn_editar = ctk.CTkButton(
            self.frame_botones,
            text="Editar",
            width=100,
            height=35,
            fg_color="#007bff",
            hover_color="#0056b3",
            command=self._abrir_formulario_editar
        )
        self.btn_editar.pack(side="left", padx=(0, 5))

        self.btn_eliminar = ctk.CTkButton(
            self.frame_botones,
            text="Eliminar",
            width=100,
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self._eliminar
        )
        self.btn_eliminar.pack(side="left", padx=(0, 5))

        self.btn_actualizar = ctk.CTkButton(
            self.frame_botones,
            text="Actualizar",
            width=100,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.actualizar
        )
        self.btn_actualizar.pack(side="left")

        # Tabla
        self.tabla = TablaPersonalizada(
            self,
            columnas=[
                ("id", "ID", 80),
                ("username", "Usuario", 150),
                ("rol", "Rol", 150)
            ],
            on_select=self._on_seleccionar,
            on_double_click=self._on_doble_clic
        )
        self.tabla.pack(fill="both", expand=True)

    def _on_seleccionar(self, item_id: str):
        """Maneja la seleccion de una fila"""
        self.usuario_seleccionado = self.tabla.obtener_id_seleccion()

    def _on_doble_clic(self, item_id: str):
        """Maneja el doble clic para editar"""
        self._abrir_formulario_editar()

    def actualizar(self):
        """Actualiza la tabla de usuarios"""
        try:
            usuarios = self.controller.listar()
            self._cargar_tabla(usuarios)
            self.usuario_seleccionado = None
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")

    def _cargar_tabla(self, usuarios: List[Usuario]):
        """Carga los usuarios en la tabla"""
        datos = []
        for usr in usuarios:
            rol_txt = "Administrador" if usr.es_admin() else "Cajero"
            datos.append((
                usr.id,
                usr.username,
                rol_txt
            ))
        
        self.tabla.cargar_datos(datos, lambda x: "normal")

    def _buscar(self, event=None):
        """Busca usuarios por nombre"""
        termino = self.entry_buscar.get().strip()
        try:
            if termino:
                usuarios = self.controller.listar()
                usuarios_filtrados = [
                    u for u in usuarios 
                    if termino.lower() in u.username.lower()
                ]
                self._cargar_tabla(usuarios_filtrados)
            else:
                self.actualizar()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")

    def _abrir_formulario_agregar(self):
        """Abre un formulario para agregar usuario"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Usuario")
        ventana.geometry("450x350")
        ventana.resizable(False, False)

        # Campos
        ctk.CTkLabel(ventana, text="Usuario:", font=ctk.CTkFont(size=12)).pack(pady=(15, 0), padx=20, anchor="w")
        entry_usuario = ctk.CTkEntry(ventana, width=400)
        entry_usuario.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Contraseña:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        entry_password = ctk.CTkEntry(ventana, width=400, show="*")
        entry_password.pack(pady=5, padx=20)

        ctk.CTkLabel(ventana, text="Rol:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
        combo_rol = ctk.CTkComboBox(
            ventana,
            values=["admin", "cajero"],
            width=400
        )
        combo_rol.set("cajero")
        combo_rol.pack(pady=5, padx=20)

        def guardar():
            try:
                username = entry_usuario.get().strip()
                password = entry_password.get().strip()
                rol = combo_rol.get()

                if not username or not password:
                    messagebox.showwarning("Validacion", "Complete los campos requeridos")
                    return

                nuevo_usuario = Usuario(
                    id=None,
                    username=username,
                    password=password,
                    rol=rol
                )
                self.controller.agregar(nuevo_usuario)
                messagebox.showinfo("Exito", "Usuario agregado correctamente")
                ventana.destroy()
                self.actualizar()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear: {str(e)}")

        ctk.CTkButton(
            ventana,
            text="Guardar",
            width=400,
            height=40,
            fg_color="#28a745",
            hover_color="#218838",
            command=guardar
        ).pack(pady=20, padx=20)

    def _abrir_formulario_editar(self):
        """Abre un formulario para editar usuario"""
        if not self.usuario_seleccionado:
            messagebox.showwarning("Atencion", "Seleccione un usuario para editar")
            return

        try:
            usuario = self.controller.buscar(self.usuario_seleccionado)
            if not usuario:
                messagebox.showerror("Error", "Usuario no encontrado")
                return

            ventana = ctk.CTkToplevel(self)
            ventana.title(f"Editar Usuario - {usuario.username}")
            ventana.geometry("450x350")
            ventana.resizable(False, False)

            # Campos
            ctk.CTkLabel(ventana, text="ID:", font=ctk.CTkFont(size=12)).pack(pady=(15, 0), padx=20, anchor="w")
            entry_id = ctk.CTkEntry(ventana, width=400)
            entry_id.insert(0, str(usuario.id))
            entry_id.configure(state="disabled")
            entry_id.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Usuario:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_usuario = ctk.CTkEntry(ventana, width=400)
            entry_usuario.insert(0, usuario.username)
            entry_usuario.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Contraseña:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            entry_password = ctk.CTkEntry(ventana, width=400, show="*")
            entry_password.insert(0, usuario.password)
            entry_password.pack(pady=5, padx=20)

            ctk.CTkLabel(ventana, text="Rol:", font=ctk.CTkFont(size=12)).pack(pady=(5, 0), padx=20, anchor="w")
            combo_rol = ctk.CTkComboBox(
                ventana,
                values=["admin", "cajero"],
                width=400
            )
            combo_rol.set(usuario.rol)
            combo_rol.pack(pady=5, padx=20)

            def guardar():
                try:
                    username = entry_usuario.get().strip()
                    password = entry_password.get().strip()
                    rol = combo_rol.get()

                    if not username or not password:
                        messagebox.showwarning("Validacion", "Complete los campos requeridos")
                        return

                    usuario.username = username
                    usuario.password = password
                    usuario.rol = rol

                    self.controller.actualizar(usuario)
                    messagebox.showinfo("Exito", "Usuario actualizado correctamente")
                    ventana.destroy()
                    self.actualizar()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar: {str(e)}")

            ctk.CTkButton(
                ventana,
                text="Guardar",
                width=400,
                height=40,
                fg_color="#007bff",
                hover_color="#0056b3",
                command=guardar
            ).pack(pady=20, padx=20)

        except Exception as e:
            messagebox.showerror("Error", f"Error al editar: {str(e)}")

    def _eliminar(self):
        """Elimina el usuario seleccionado"""
        if not self.usuario_seleccionado:
            messagebox.showwarning("Atencion", "Seleccione un usuario para eliminar")
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"Desea eliminar el usuario seleccionado?"
        ):
            return

        try:
            self.controller.eliminar(self.usuario_seleccionado)
            messagebox.showinfo("Exito", "Usuario eliminado correctamente")
            self.actualizar()
        except Exception as e:
            messagebox.showerror("Error", str(e))
