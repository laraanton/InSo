# src/vista/softrip_style.py
# Estilos visuales de la aplicación Softrip (administración)

_BG          = "#f9f7f2"
_SIDEBAR     = "#333333"
_SIDEBAR_HVR = "#3a3a3a"
_SIDEBAR_ACT = "#3d5a5a"
_TEAL        = "#5e8d8d"
_OLIVE       = "#7a8c4e"
_AMBER       = "#b08a4e"
_WHITE       = "#FFFFFF"
_TEXT        = "#333333"
_TEXT2       = "#666666"
_BORDER      = "#e8e4dc"
_RED         = "#c0392b"
_GREEN       = "#27ae60"

SOFTRIP_STYLE = f"""

/* BASE */
QMainWindow, QWidget#centralwidget,
QWidget#pageDashboard, QWidget#pageOperadores,
QWidget#pageUsuarios, QWidget#pageActividad, QWidget#pageSistema {{
    background-color: {_BG};
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: {_TEXT};
}}

/* SIDEBAR */
QFrame#sidebarFrame {{
    background-color: {_SIDEBAR};
    border: none;
}}
QFrame#logoFrame {{
    background-color: #2b2b2b;
    border-bottom: 1px solid #444444;
    min-height: 72px;
    max-height: 72px;
}}
QLabel#logoLabel {{
    color: {_TEAL};
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 3px;
    padding: 0 16px;
}}

/* Botones nav sidebar */
QFrame#sidebarFrame QPushButton {{
    background-color: transparent;
    color: #999999;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 13px 20px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 0px;
}}
QFrame#sidebarFrame QPushButton:hover {{
    background-color: {_SIDEBAR_HVR};
    color: #dddddd;
    border-left: 3px solid #555555;
}}
QFrame#sidebarFrame QPushButton[active=true] {{
    background-color: {_SIDEBAR_ACT};
    color: {_TEAL};
    border-left: 3px solid {_TEAL};
    font-weight: 600;
}}
QFrame#sidebarFrame QPushButton#btnLogout {{
    color: #e05252;
    border-top: 1px solid #444444;
    border-left: 3px solid transparent;
    margin-top: 4px;
}}
QFrame#sidebarFrame QPushButton#btnLogout:hover {{
    background-color: #3a2020;
    color: #ff7070;
    border-left: 3px solid {_RED};
}}
QLabel#sidebarFooter {{
    color: #555555;
    font-size: 10px;
    font-style: italic;
    letter-spacing: 0.8px;
    padding: 10px 8px;
}}

/* TOPBAR */
QFrame#topbarFrame {{
    background-color: {_WHITE};
    border-bottom: 1px solid {_BORDER};
    min-height: 64px;
    max-height: 64px;
}}
QLabel#pageTitle {{
    color: {_TEXT};
    font-size: 17px;
    font-weight: 700;
}}
QLabel#pageBreadcrumb {{
    color: {_TEXT2};
    font-size: 11px;
}}
QLabel#avatarLabel {{
    background-color: {_TEAL};
    color: {_WHITE};
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-weight: 700;
    font-size: 13px;
}}
QLabel#adminNameLabel {{
    color: {_TEXT};
    font-size: 13px;
    font-weight: 600;
    margin-left: 8px;
}}

/* TARJETAS MÉTRICAS */
QFrame#cardOperadores, QFrame#cardClientes,
QFrame#cardBloqueados, QFrame#cardTotal {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-radius: 8px;
    padding: 16px;
}}
QFrame#cardOperadores {{ border-top: 3px solid {_TEAL};  }}
QFrame#cardClientes   {{ border-top: 3px solid {_OLIVE}; }}
QFrame#cardBloqueados {{ border-top: 3px solid {_RED};   }}
QFrame#cardTotal      {{ border-top: 3px solid {_AMBER}; }}

QLabel#lblCardOpTitulo, QLabel#lblCardClTitulo,
QLabel#lblCardBlTitulo, QLabel#lblCardTotTitulo {{
    color: {_TEXT2};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
}}
QLabel#lblTotalOperadores, QLabel#lblTotalClientes,
QLabel#lblTotalBloqueados, QLabel#lblTotalUsuarios {{
    color: {_TEXT};
    font-size: 34px;
    font-weight: 800;
}}
QLabel#lblCardOpSub, QLabel#lblCardClSub,
QLabel#lblCardBlSub, QLabel#lblCardTotSub {{
    color: {_TEXT2};
    font-size: 11px;
}}

/* TÍTULOS DE SECCIÓN */
QLabel#lblDashActTitle, QLabel#lblHistorialTitle,
QLabel#lblBackupTitle, QLabel#lblSysTitle {{
    color: {_TEXT};
    font-size: 14px;
    font-weight: 700;
}}

/* TABLAS */
QTableWidget {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-radius: 8px;
    gridline-color: transparent;
    outline: none;
    font-size: 13px;
    color: {_TEXT};
    selection-background-color: #eef4f4;
    selection-color: {_TEAL};
}}
QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid #f3f0ea;
}}
QTableWidget::item:selected {{
    background-color: #eef4f4;
    color: {_TEAL};
}}
QHeaderView::section {{
    background-color: {_BG};
    color: {_TEXT2};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.1px;
    padding: 9px 14px;
    border: none;
    border-bottom: 2px solid {_BORDER};
}}
QTableWidget QTableCornerButton::section {{
    background-color: {_BG};
    border: none;
}}
QScrollBar:vertical {{
    background: {_BG}; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: #cac5bc; border-radius: 3px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {_BG}; height: 6px; border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: #cac5bc; border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

/* QLINEEDIT */
QLineEdit {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {_TEXT};
}}
QLineEdit:hover {{ border-color: #c8c0b4; }}
QLineEdit:focus {{ border: 1.5px solid {_TEAL}; background-color: #fafaf8; }}
QLineEdit:disabled {{ background-color: #f0ede6; color: #aaaaaa; }}

/* QCOMBOBOX */
QComboBox {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    color: {_TEXT};
    min-width: 150px;
}}
QComboBox:hover {{ border-color: #c8c0b4; }}
QComboBox:focus {{ border: 1.5px solid {_TEAL}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    outline: none;
    selection-background-color: #eef4f4;
    selection-color: {_TEAL};
    font-size: 13px;
}}
QComboBox QAbstractItemView::item {{ padding: 7px 12px; }}
QComboBox QAbstractItemView::item:hover {{ background-color: #f4fafa; }}

/* CARDS SISTEMA */
QFrame#backupCard {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-top: 3px solid {_TEAL};
    border-radius: 8px;
    padding: 20px;
}}
QFrame#infoSistemaCard {{
    background-color: {_WHITE};
    border: 1px solid {_BORDER};
    border-top: 3px solid {_OLIVE};
    border-radius: 8px;
    padding: 20px;
}}
QLabel#lblBackupDesc, QLabel#lblPython, QLabel#lblHost, QLabel#bkLast1 {{
    color: {_TEXT2};
    font-size: 12px;
}}

/* BOTONES NAMED */
QPushButton#btnNuevoOperador {{
    background-color: {_TEAL};
    color: {_WHITE};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#btnNuevoOperador:hover {{ background-color: #4e7a7a; }}

QPushButton#btnExportarOp {{
    background-color: {_OLIVE};
    color: {_WHITE};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#btnExportarOp:hover {{ background-color: #697a3e; }}

QPushButton#btnVerTodosDash {{
    background-color: {_WHITE};
    color: {_TEAL};
    border: 1px solid {_TEAL};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#btnVerTodosDash:hover {{ background-color: #eef4f4; }}

QPushButton#btnBackupAhora {{
    background-color: {_TEAL};
    color: {_WHITE};
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
}}
QPushButton#btnBackupAhora:hover {{ background-color: #4e7a7a; }}

/* BOTONES INLINE DE TABLA */
QPushButton#btnEdit {{
    background-color: #eef4f4;
    color: {_TEAL};
    border: 1px solid #c5dcdc;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#btnEdit:hover {{ background-color: #d4e8e8; }}

QPushButton#btnDanger {{
    background-color: #fdecea;
    color: {_RED};
    border: 1px solid #f5c6c3;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#btnDanger:hover {{ background-color: #f9d4d1; }}

QPushButton#btnSuccess {{
    background-color: #eafaf1;
    color: {_GREEN};
    border: 1px solid #b7e4c7;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#btnSuccess:hover {{ background-color: #d4f0e0; }}

QPushButton#btnSecondary {{
    background-color: {_WHITE};
    color: {_TEXT};
    border: 1px solid {_BORDER};
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
}}
QPushButton#btnSecondary:hover {{ border-color: {_TEAL}; color: {_TEAL}; }}

/* FOOTER SIDEBAR */
QLabel#sidebarFooter {{
    color: #555555;
    font-size: 10px;
    font-style: italic;
    letter-spacing: 0.8px;
    padding: 10px 8px;
}}
"""