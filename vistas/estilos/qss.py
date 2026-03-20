"""Stylesheet global de PyQt6 para el sistema."""

from pathlib import Path

from . import colores


def get_global_stylesheet() -> str:
    arrow_icon = (Path(__file__).resolve().parent / "assets" / "combobox_arrow_down.svg").as_posix()
    return f"""
QMainWindow, QWidget {{
    background-color: {colores.BACKGROUND};
    color: {colores.TEXT_PRIMARY};
    font-family: 'Segoe UI';
    font-size: 13px;
}}

QLabel {{
    color: {colores.TEXT_PRIMARY};
}}

QPushButton {{
    border-radius: 8px;
    border: none;
    padding: 8px 16px;
    background-color: {colores.SURFACE_LIGHT};
    color: {colores.TEXT_PRIMARY};
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: #3A3A3A;
}}
QPushButton:pressed {{
    background-color: #262626;
}}
QPushButton[variant="primary"], QPushButton[class="btn-primary"] {{
    background-color: {colores.PRIMARY};
}}
QPushButton[variant="primary"]:hover, QPushButton[class="btn-primary"]:hover {{
    background-color: {colores.PRIMARY_DARK};
}}
QPushButton[variant="primary"]:pressed, QPushButton[class="btn-primary"]:pressed {{
    background-color: #002A66;
}}
QPushButton[variant="danger"], QPushButton[class="btn-danger"] {{
    background-color: {colores.DANGER};
}}
QPushButton[variant="danger"]:hover, QPushButton[class="btn-danger"]:hover {{
    background-color: #A71F1F;
}}
QPushButton[variant="success"], QPushButton[class="btn-success"] {{
    background-color: {colores.SUCCESS};
}}
QPushButton[variant="success"]:hover, QPushButton[class="btn-success"]:hover {{
    background-color: #246428;
}}
QPushButton[variant="warning"], QPushButton[class="btn-warning"] {{
    background-color: {colores.WARNING};
    color: #1A1A1A;
}}
QPushButton[variant="warning"]:hover, QPushButton[class="btn-warning"]:hover {{
    background-color: #D66E0C;
}}
QPushButton[class="btn-neutral"] {{
    background-color: #5A5A5A;
}}
QPushButton[class="btn-neutral"]:hover {{
    background-color: #6C6C6C;
}}
QPushButton[class="btn-purple"] {{
    background-color: #6f42c1;
    color: white;
}}
QPushButton[class="btn-purple"]:hover {{
    background-color: #5e37a7;
}}
QPushButton[class="btn-purple"]:pressed {{
    background-color: #4b2c86;
}}

QLineEdit, QComboBox {{
    border: 1px solid {colores.BORDER};
    border-radius: 6px;
    padding: 8px 32px 8px 8px;
    background-color: {colores.SURFACE_LIGHT};
    color: {colores.TEXT_PRIMARY};
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {colores.PRIMARY};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border: none;
    background: transparent;
    padding-right: 6px;
}}
QComboBox::down-arrow {{
    image: url({arrow_icon});
    width: 12px;
    height: 8px;
}}

QTableWidget {{
    background-color: {colores.SURFACE};
    alternate-background-color: {colores.SURFACE_LIGHT};
    color: {colores.TEXT_PRIMARY};
    gridline-color: transparent;
    selection-background-color: {colores.PRIMARY_LIGHT};
    selection-color: white;
    border: 1px solid {colores.BORDER};
    border-radius: 8px;
}}
QHeaderView::section {{
    background-color: {colores.PRIMARY};
    color: white;
    font-weight: 700;
    padding: 8px;
    border: none;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: #4A4A4A;
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: #6A6A6A;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0;
    background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #4A4A4A;
    min-width: 30px;
    border-radius: 5px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    width: 0;
    background: none;
}}

QFrame[class="card"] {{
    background-color: {colores.SURFACE};
    border-radius: 12px;
    padding: 16px;
    border: 1px solid {colores.BORDER};
}}

QTabWidget::pane {{
    border: 1px solid {colores.BORDER};
    border-radius: 10px;
    top: -1px;
    background-color: {colores.SURFACE};
}}
QTabBar::tab {{
    background-color: transparent;
    color: {colores.TEXT_SECONDARY};
    padding: 10px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    min-width: 110px;
}}
QTabBar::tab:selected {{
    color: {colores.TEXT_PRIMARY};
    border-bottom: 2px solid {colores.PRIMARY};
}}
QTabBar::tab:hover {{
    color: {colores.TEXT_PRIMARY};
    background-color: rgba(255, 255, 255, 0.04);
}}
"""
