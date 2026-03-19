"""
Componente de Entrada con Autocompletado
"""
import customtkinter as ctk
from typing import List, Callable, Optional


class EntryConAutoCompletado(ctk.CTkEntry):
    """Entrada de texto con sugerencias de autocompletado"""

    def __init__(
        self,
        master,
        obtener_opciones: Callable[[str], List[str]],
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.obtener_opciones = obtener_opciones
        self.opciones_coincidentes: List[str] = []
        self.ventana_lista = None
        self.listbox = None

        # Bind de eventos
        self.bind("<KeyRelease>", self._en_tecla_soltada)
        self.bind("<FocusOut>", self._ocultar_lista)
        self.bind("<Down>", self._navegar_lista)
        self.bind("<Up>", self._navegar_lista)
        self.bind("<Return>", self._seleccionar_opcion)

    def _en_tecla_soltada(self, event=None):
        """Se ejecuta cuando se suelta una tecla"""
        texto = self.get().strip()

        if not texto:
            self._ocultar_lista()
            return

        # Obtener opciones que coinciden
        try:
            todas_opciones = self.obtener_opciones(texto)
            self.opciones_coincidentes = [
                opt for opt in todas_opciones
                if texto.lower() in opt.lower()
            ][:5]  # Mostrar máximo 5 opciones
        except:
            self.opciones_coincidentes = []

        if self.opciones_coincidentes:
            self._mostrar_lista()
        else:
            self._ocultar_lista()

    def _mostrar_lista(self):
        """Muestra la ventana con las opciones"""
        if not self.opciones_coincidentes:
            return

        # Crear ventana emergente si no existe
        if self.ventana_lista is None:
            self.ventana_lista = ctk.CTkToplevel(self.master)
            self.ventana_lista.geometry("250x150")
            self.ventana_lista.resizable(False, False)

            # Listbox con opciones
            self.listbox = ctk.CTkTextbox(
                self.ventana_lista,
                width=250,
                height=150
            )
            self.listbox.pack(fill="both", expand=True)

        # Limpiar y actualizar listbox
        self.listbox.delete("1.0", "end")
        for opcion in self.opciones_coincidentes:
            self.listbox.insert("end", opcion + "\n")

        # Posicionar debajo del entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.ventana_lista.geometry(f"+{x}+{y}")
        self.ventana_lista.lift()

    def _ocultar_lista(self, event=None):
        """Oculta la ventana con las opciones"""
        if self.ventana_lista:
            self.ventana_lista.withdraw()

    def _navegar_lista(self, event):
        """Navega en la lista de opciones"""
        if self.ventana_lista and self.listbox:
            self.ventana_lista.lift()

    def _seleccionar_opcion(self, event=None):
        """Selecciona una opción de la lista"""
        if self.ventana_lista and self.listbox and self.opciones_coincidentes:
            self.delete(0, "end")
            self.insert(0, self.opciones_coincidentes[0])
            self._ocultar_lista()

    def obtener_valor(self) -> str:
        """Obtiene el valor actual del entry"""
        return self.get().strip()
