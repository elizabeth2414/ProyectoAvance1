"""
Vista Factura - Generacion de facturas en PDF
"""
import os
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def generar_factura_pdf(conexion, venta_id: str) -> str:
    """
    Genera una factura PDF para una venta especifica.

    Args:
        conexion: Conexion a la base de datos SQLite
        venta_id: ID de la venta

    Returns:
        Ruta del archivo PDF generado o None si se cancela
    """
    from controladores.venta_controller import VentaController

    # Obtener datos de la factura
    venta_ctrl = VentaController(conexion)

    try:
        datos = venta_ctrl.generar_datos_factura(venta_id)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudo obtener datos de la venta:\n{str(e)}")
        return None

    # Dialogo para guardar archivo
    nombre_default = f"Factura_{venta_id}_{datetime.now().strftime('%Y%m%d')}.pdf"

    ruta_archivo, _ = QFileDialog.getSaveFileName(
        None,
        "Guardar Factura PDF",
        nombre_default,
        "Archivo PDF (*.pdf)"
    )

    if not ruta_archivo:
        return None

    try:
        _crear_pdf(ruta_archivo, datos)
        QMessageBox.information(None, "Factura Generada", f"Factura guardada exitosamente:\n{ruta_archivo}")
        return ruta_archivo

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al generar PDF:\n{str(e)}")
        return None


def _crear_pdf(ruta_archivo: str, datos: dict):
    """Crea el documento PDF con los datos de la factura"""

    # Crear documento
    doc = SimpleDocTemplate(
        ruta_archivo,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Estilos
    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=estilos['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1f538d')
    )

    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=estilos['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )

    estilo_normal = ParagraphStyle(
        'Normal',
        parent=estilos['Normal'],
        fontSize=11,
        spaceAfter=5
    )

    estilo_footer = ParagraphStyle(
        'Footer',
        parent=estilos['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    # Elementos del PDF
    elementos = []

    # ===== ENCABEZADO =====
    # Logo de texto
    logo_texto = """
    <para align="center">
    <font size="12" color="#666666">SISTEMA DE GESTION DE VENTAS</font>
    </para>
    """
    elementos.append(Paragraph(logo_texto, estilos['Normal']))
    elementos.append(Spacer(1, 10))

    # Titulo
    elementos.append(Paragraph("FACTURA DE VENTA", estilo_titulo))

    # ===== INFORMACION DE FACTURA =====
    info_factura = [
        ['Numero de Factura:', datos['venta_id']],
        ['Fecha de Emision:', datos['fecha']],
        ['Estado:', datos['estado'].upper()]
    ]

    tabla_info = Table(info_factura, colWidths=[4*cm, 6*cm])
    tabla_info.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f538d')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabla_info)
    elementos.append(Spacer(1, 20))

    # ===== DATOS DEL CLIENTE =====
    elementos.append(Paragraph("DATOS DEL CLIENTE", estilo_subtitulo))

    cliente = datos['cliente']
    datos_cliente = [
        ['ID Cliente:', cliente['id']],
        ['Nombre:', cliente['nombre'] or 'N/A'],
        ['Correo:', cliente['correo'] or 'N/A'],
        ['Telefono:', cliente['telefono'] or 'N/A'],
        ['Direccion:', cliente['direccion'] or 'N/A']
    ]

    tabla_cliente = Table(datos_cliente, colWidths=[3*cm, 10*cm])
    tabla_cliente.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
    ]))
    elementos.append(tabla_cliente)
    elementos.append(Spacer(1, 20))

    # ===== DETALLE DE PRODUCTOS =====
    elementos.append(Paragraph("DETALLE DE LA VENTA", estilo_subtitulo))

    producto = datos['producto']

    # Cabecera y datos de la tabla
    encabezados = ['Producto', 'Cantidad', 'Precio Unit.', 'Desc.%', 'Subtotal']
    fila_producto = [
        producto['nombre'],
        str(int(datos['cantidad'])),
        f"S/ {producto['precio']:.2f}",
        f"{datos['descuento_porcentaje']}%",
        f"S/ {datos['subtotal']:.2f}"
    ]

    tabla_productos = Table(
        [encabezados, fila_producto],
        colWidths=[6*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm]
    )
    tabla_productos.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f538d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(tabla_productos)
    elementos.append(Spacer(1, 20))

    # ===== TOTALES =====
    totales = [
        ['Subtotal:', f"S/ {datos['subtotal']:.2f}"],
        ['Descuento Aplicado:', f"- S/ {datos['descuento_monto']:.2f}"],
        ['TOTAL FINAL:', f"S/ {datos['total']:.2f}"]
    ]

    tabla_totales = Table(totales, colWidths=[10*cm, 5*cm])
    tabla_totales.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 11),
        ('FONTSIZE', (0, 2), (-1, 2), 14),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#1f538d')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 2), (-1, 2), 2, colors.HexColor('#1f538d')),
    ]))
    elementos.append(tabla_totales)
    elementos.append(Spacer(1, 40))

    # ===== PIE DE PAGINA =====
    elementos.append(Paragraph("=" * 60, estilo_footer))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("Gracias por su compra", estilo_footer))
    elementos.append(Paragraph(
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        estilo_footer
    ))
    elementos.append(Paragraph("Sistema de Gestion de Ventas v1.0", estilo_footer))

    # Construir PDF
    doc.build(elementos)
