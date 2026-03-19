"""
Formularios reutilizables con CustomTkinter
"""
import customtkinter as ctk
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class CampoFormulario:
    """Definicion de un campo de formulario"""
    nombre: str
    etiqueta: str
    tipo: str = "texto"  # texto, numero, combo, slider
    requerido: bool = False
    valor_default: Any = ""
    opciones: List[str] = None  # Para combobox
    rango: Tuple[float, float] = (0, 100)  # Para slider
    ancho: int = 250
    readonly: bool = False


class FormularioBase(ctk.CTkToplevel):
    """Ventana de formulario reutilizable"""

    def __init__(
        self,
        parent,
        titulo: str,
        campos: List[CampoFormulario],
        on_guardar: Callable[[Dict[str, Any]], bool],
        datos_iniciales: Optional[Dict[str, Any]] = None,
        modo_edicion: bool = False,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.campos = campos
        self.on_guardar = on_guardar
        self.datos_iniciales = datos_iniciales or {}
        self.modo_edicion = modo_edicion
        self.widgets_campos: Dict[str, Any] = {}
        self.resultado = None

        # Configuracion ventana
        self.title(titulo)
        altura_minima = max(600, 150 + len(campos) * 75)
        self.geometry("500x" + str(altura_minima))
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        self._crear_widgets()
        self._cargar_datos_iniciales()

    def _crear_widgets(self):
        """Crea los widgets del formulario"""
        # Container principal que tendrá campos y botones
        self.frame_container = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_container.pack(fill="both", expand=True)

        # Frame de campos scrolleable
        self.frame_campos_scroll = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.frame_campos_scroll.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Crear campos
        for i, campo in enumerate(self.campos):
            frame_campo = ctk.CTkFrame(self.frame_campos_scroll, fg_color="transparent")
            frame_campo.pack(fill="x", pady=5)

            # Etiqueta
            etiqueta_texto = campo.etiqueta
            if campo.requerido:
                etiqueta_texto += " *"

            lbl = ctk.CTkLabel(
                frame_campo,
                text=etiqueta_texto,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            lbl.pack(fill="x")

            # Widget segun tipo
            if campo.tipo == "texto":
                widget = ctk.CTkEntry(
                    frame_campo,
                    width=campo.ancho,
                    height=35,
                    state="disabled" if campo.readonly else "normal"
                )
                widget.pack(fill="x", pady=(2, 0))

            elif campo.tipo == "numero":
                widget = ctk.CTkEntry(
                    frame_campo,
                    width=campo.ancho,
                    height=35,
                    state="disabled" if campo.readonly else "normal"
                )
                widget.pack(fill="x", pady=(2, 0))

            elif campo.tipo == "combo":
                widget = ctk.CTkComboBox(
                    frame_campo,
                    width=campo.ancho,
                    height=35,
                    values=campo.opciones or [],
                    state="disabled" if campo.readonly else "normal"
                )
                widget.pack(fill="x", pady=(2, 0))

            elif campo.tipo == "slider":
                frame_slider = ctk.CTkFrame(frame_campo, fg_color="transparent")
                frame_slider.pack(fill="x", pady=(2, 0))

                widget = ctk.CTkSlider(
                    frame_slider,
                    from_=campo.rango[0],
                    to=campo.rango[1],
                    width=campo.ancho - 60,
                    command=lambda v, c=campo.nombre: self._actualizar_label_slider(c, v)
                )
                widget.pack(side="left", padx=(0, 10))

                lbl_valor = ctk.CTkLabel(
                    frame_slider,
                    text=f"{campo.valor_default}%",
                    width=50
                )
                lbl_valor.pack(side="left")
                self.widgets_campos[f"{campo.nombre}_label"] = lbl_valor

            elif campo.tipo == "textarea":
                widget = ctk.CTkTextbox(
                    frame_campo,
                    width=campo.ancho,
                    height=80,
                    state="disabled" if campo.readonly else "normal"
                )
                widget.pack(fill="x", pady=(2, 0))

            self.widgets_campos[campo.nombre] = widget

        # Label de error - en el frame de campos
        self.lbl_error = ctk.CTkLabel(
            self.frame_campos_scroll,
            text="",
            text_color="#FF6B6B",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_error.pack(fill="x", pady=(10, 0))

        # Frame botones - SIEMPRE VISIBLE EN EL BOTTOM
        self.frame_botones = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.frame_botones.pack(fill="x", padx=20, pady=20)

        # Separator
        separator = ctk.CTkFrame(self.frame_botones, height=1, fg_color="#3a3a3a")
        separator.pack(fill="x", pady=(0, 15))

        self.btn_cancelar = ctk.CTkButton(
            self.frame_botones,
            text="Cancelar",
            width=120,
            height=40,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._cancelar
        )
        self.btn_cancelar.pack(side="left", padx=(0, 10))

        texto_guardar = "✓ Guardar Cambios" if self.modo_edicion else "✓ Guardar"
        self.btn_guardar = ctk.CTkButton(
            self.frame_botones,
            text=texto_guardar,
            width=140,
            height=40,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._guardar
        )
        self.btn_guardar.pack(side="right")

    def _actualizar_label_slider(self, nombre_campo: str, valor: float):
        """Actualiza el label del slider"""
        label_key = f"{nombre_campo}_label"
        if label_key in self.widgets_campos:
            self.widgets_campos[label_key].configure(text=f"{int(valor)}%")

    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en los campos"""
        for campo in self.campos:
            if campo.nombre in self.datos_iniciales:
                valor = self.datos_iniciales[campo.nombre]
                widget = self.widgets_campos[campo.nombre]

                if campo.tipo in ["texto", "numero"]:
                    # Permitir edicion temporal si está disabled
                    was_disabled = widget.cget("state") == "disabled"
                    if was_disabled:
                        widget.configure(state="normal")
                    
                    widget.delete(0, "end")
                    widget.insert(0, str(valor) if valor else "")
                    
                    if was_disabled:
                        widget.configure(state="disabled")
                        
                elif campo.tipo == "combo":
                    if valor:
                        widget.set(str(valor))
                elif campo.tipo == "slider":
                    widget.set(float(valor) if valor else campo.rango[0])
                    self._actualizar_label_slider(campo.nombre, float(valor) if valor else 0)
                elif campo.tipo == "textarea":
                    was_disabled = widget.cget("state") == "disabled"
                    if was_disabled:
                        widget.configure(state="normal")
                    
                    widget.delete("1.0", "end")
                    widget.insert("1.0", str(valor) if valor else "")
                    
                    if was_disabled:
                        widget.configure(state="disabled")
            elif campo.valor_default:
                widget = self.widgets_campos[campo.nombre]
                if campo.tipo in ["texto", "numero"]:
                    widget.insert(0, str(campo.valor_default))
                elif campo.tipo == "combo":
                    widget.set(str(campo.valor_default))
                elif campo.tipo == "slider":
                    widget.set(float(campo.valor_default))

    def _validar(self) -> Tuple[bool, str]:
        """Valida los campos del formulario"""
        for campo in self.campos:
            if campo.requerido:
                valor = self._obtener_valor(campo.nombre, campo.tipo)
                if not valor or (isinstance(valor, str) and not valor.strip()):
                    return False, f"El campo '{campo.etiqueta}' es requerido"

            if campo.tipo == "numero":
                valor = self._obtener_valor(campo.nombre, campo.tipo)
                if valor:
                    try:
                        float(valor)
                    except ValueError:
                        return False, f"El campo '{campo.etiqueta}' debe ser un numero"

        return True, ""

    def _obtener_valor(self, nombre: str, tipo: str) -> Any:
        """Obtiene el valor de un campo"""
        widget = self.widgets_campos[nombre]
        if tipo in ["texto", "numero"]:
            # Permitir lectura de campos disabled
            return widget.get()
        elif tipo == "combo":
            return widget.get()
        elif tipo == "slider":
            return widget.get()
        elif tipo == "textarea":
            return widget.get("1.0", "end-1c")
        return None

    def _guardar(self):
        """Valida y guarda el formulario"""
        valido, mensaje = self._validar()
        if not valido:
            self.lbl_error.configure(text=mensaje)
            return

        # Recopilar datos
        datos = {}
        for campo in self.campos:
            valor = self._obtener_valor(campo.nombre, campo.tipo)
            if campo.tipo == "numero" and valor:
                try:
                    valor = float(valor)
                    if valor == int(valor):
                        valor = int(valor)
                except:
                    pass
            datos[campo.nombre] = valor

        # Llamar callback
        try:
            if self.on_guardar(datos):
                self.resultado = datos
                self.destroy()
            else:
                self.lbl_error.configure(text="Error al guardar los datos")
        except Exception as e:
            self.lbl_error.configure(text=str(e))

    def _cancelar(self):
        """Cierra el formulario sin guardar"""
        self.resultado = None
        self.destroy()

    def obtener_resultado(self) -> Optional[Dict[str, Any]]:
        """Retorna el resultado del formulario"""
        return self.resultado
