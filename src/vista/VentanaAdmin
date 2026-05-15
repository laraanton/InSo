import sys
import platform
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QTableWidgetItem,
    QPushButton, QHBoxLayout, QWidget, QDialog, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QFormLayout, QDialogButtonBox,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from src.modelo.Logica_login import BussinessObject
from src.modelo.dao.UserDAO import UserDAO

Form, Window = uic.loadUiType("./src/vista/ui/vistaAdmin.ui")

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


class DialogoOperador(QDialog):
    """Formulario modal para registrar o editar un operador."""
    STYLE = f"""
        QDialog {{ background-color: #F5F0E8; font-family: 'Segoe UI'; }}
        QLabel  {{ color: #333333; font-size: 12px; }}
        QLabel#dlgTitle {{
            color: #2C2C2C; font-size: 16px;
            font-weight: bold; font-family: 'Georgia';
        }}
        QLineEdit, QComboBox {{
            background-color: #FFFFFF;
            border: 1px solid #DDD5C5;
            border-radius: 6px;
            padding: 7px 10px;
            font-size: 12px;
            color: #333333;
        }}
        QLineEdit:focus, QComboBox:focus {{ border: 1px solid {_TEAL}; }}
        QDialogButtonBox QPushButton {{
            padding: 8px 20px; border-radius: 6px;
            font-size: 12px; font-weight: bold;
        }}
        QDialogButtonBox QPushButton[text="Guardar"] {{
            background-color: {_TEAL}; color: white; border: none;
        }}
        QDialogButtonBox QPushButton[text="Cancelar"] {{
            background-color: transparent; color: #666;
            border: 1px solid #CCC;
        }}
    """

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Operador" if not usuario else "Editar Operador")
        self.setMinimumWidth(440)
        self.setStyleSheet(self.STYLE)
        self._build_ui(usuario)

    def _build_ui(self, usuario):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(28, 24, 28, 24)

        titulo = QLabel("Nuevo Operador" if not usuario else "Editar Operador")
        titulo.setObjectName("dlgTitle")
        lay.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.in_dni      = QLineEdit()
        self.in_nombre   = QLineEdit()
        self.in_email    = QLineEdit()
        self.in_telefono = QLineEdit()
        self.in_password = QLineEdit()
        self.in_password.setEchoMode(QLineEdit.Password)
        self.in_password.setPlaceholderText(
            "Dejar vacío para no cambiar" if usuario else "Mínimo 6 caracteres"
        )

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Activo", "Inactivo", "Suspendido"])

        for w, ph in [
            (self.in_dni,      "Ej: 12345678A"),
            (self.in_nombre,   "Nombre completo"),
            (self.in_email,    "correo@softrip.es"),
            (self.in_telefono, "Opcional"),
        ]:
            w.setPlaceholderText(ph)

        if usuario:
            self.in_dni.setText(usuario.dni_nie or "")
            self.in_nombre.setText(usuario.nombre_completo or "")
            self.in_email.setText(usuario.email or "")
            self.in_telefono.setText(usuario.telefono or "")
            idx = self.cb_estado.findText(usuario.estado)
            if idx >= 0:
                self.cb_estado.setCurrentIndex(idx)

        form.addRow("DNI / NIE *",       self.in_dni)
        form.addRow("Nombre completo *",  self.in_nombre)
        form.addRow("Email *",            self.in_email)
        form.addRow("Teléfono",           self.in_telefono)
        form.addRow("Contraseña *",       self.in_password)
        form.addRow("Estado",             self.cb_estado)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Save).setText("Guardar")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def datos(self):
        return {
            "dni_nie":         self.in_dni.text().strip(),
            "nombre_completo": self.in_nombre.text().strip(),
            "email":           self.in_email.text().strip(),
            "telefono":        self.in_telefono.text().strip(),
            "password":        self.in_password.text().strip(),
            "estado":          self.cb_estado.currentText(),
        }


class VentanaAdmin(QMainWindow, Form):

    PAGE_DASHBOARD  = 0
    PAGE_OPERADORES = 1
    PAGE_USUARIOS   = 2
    PAGE_ACTIVIDAD  = 3
    PAGE_SISTEMA    = 4

    ESTADO_COLORES = {
        "Activo":     ("#dcfce7", "#166534"),
        "Bloqueado":  ("#fee2e2", "#991b1b"),
        "Suspendido": ("#fef3c7", "#92400e"),
        "Inactivo":   ("#F3E5F5", "#6A1B9A"),
    }

    def __init__(self, usuario_actual):
        super().__init__()
        self.setupUi(self)
        self.usuario_actual = usuario_actual
        self.logica = BussinessObject()
        self.dao    = UserDAO()
        self._backup_log = []

        self._configurar_ui()
        self._conectar_senales()
        self._navegar(self.PAGE_DASHBOARD)

    def _configurar_ui(self):
        self.setStyleSheet(SOFTRIP_STYLE)

        nombre  = self.usuario_actual.nombre_completo or "Admin"
        inicial = nombre[0].upper()
        self.avatarLabel.setText(inicial)
        self.adminNameLabel.setText(nombre)

        for tabla, modos in [
            (self.tablaOperadores,    [40, 180, 110, 200, 110, 90, 100, 120]),
            (self.tablaUsuarios,      [40, 170, 110, 190, 100, 90, 110, 120]),
            (self.tablaActividad,     [100, 70, 150, 90, 120, 220, 110]),
            (self.tablaDashActividad, [130, 160, 100, None]),
            (self.tablaBackups,       [160, 220, 80, 80, 100]),
        ]:
            header = tabla.horizontalHeader()
            for i, w in enumerate(modos):
                if w is None:
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    tabla.setColumnWidth(i, w)
            tabla.verticalHeader().setDefaultSectionSize(38)
            tabla.setSelectionMode(QAbstractItemView.SingleSelection)

        self.lblPython.setText(f"Python:  {platform.python_version()}")
        self.lblHost.setText(f"Host BD:  PORTATILMARTA\\SQLEXPRESS")

    def _conectar_senales(self):
        self.btnNavDashboard.clicked.connect(lambda: self._navegar(self.PAGE_DASHBOARD))
        self.btnNavOperadores.clicked.connect(lambda: self._navegar(self.PAGE_OPERADORES))
        self.btnNavUsuarios.clicked.connect(lambda: self._navegar(self.PAGE_USUARIOS))
        self.btnNavActividad.clicked.connect(lambda: self._navegar(self.PAGE_ACTIVIDAD))
        self.btnNavSistema.clicked.connect(lambda: self._navegar(self.PAGE_SISTEMA))
        self.btnLogout.clicked.connect(self._cerrar_sesion)

        self.btnVerTodosDash.clicked.connect(lambda: self._navegar(self.PAGE_ACTIVIDAD))

        self.btnNuevoOperador.clicked.connect(self._nuevo_operador)
        self.searchOperadores.textChanged.connect(self._filtrar_operadores)
        self.filtroEstadoOp.currentTextChanged.connect(self._filtrar_operadores)
        self.btnExportarOp.clicked.connect(self._exportar_operadores)

        self.searchUsuarios.textChanged.connect(self._filtrar_usuarios)
        self.filtroTipoUs.currentTextChanged.connect(self._filtrar_usuarios)
        self.filtroEstadoUs.currentTextChanged.connect(self._filtrar_usuarios)

        self.filtroAccion.currentTextChanged.connect(self._filtrar_actividad)
        self.btnBackupAhora.clicked.connect(self._hacer_backup)

    def _navegar(self, pagina):
        self.stackedWidget.setCurrentIndex(pagina)

        titulos = {
            self.PAGE_DASHBOARD:  ("Dashboard",             "Softrip › Administración"),
            self.PAGE_OPERADORES: ("Gestión de Operadores", "Softrip › Administración › Operadores"),
            self.PAGE_USUARIOS:   ("Todos los Usuarios",    "Softrip › Administración › Usuarios"),
            self.PAGE_ACTIVIDAD:  ("Registro de Actividad", "Softrip › Administración › Actividad"),
            self.PAGE_SISTEMA:    ("Sistema y Backups",      "Softrip › Administración › Sistema"),
        }
        self.pageTitle.setText(titulos[pagina][0])
        self.pageBreadcrumb.setText(titulos[pagina][1])

        botones = {
            self.PAGE_DASHBOARD:  self.btnNavDashboard,
            self.PAGE_OPERADORES: self.btnNavOperadores,
            self.PAGE_USUARIOS:   self.btnNavUsuarios,
            self.PAGE_ACTIVIDAD:  self.btnNavActividad,
            self.PAGE_SISTEMA:    self.btnNavSistema,
        }
        for p, btn in botones.items():
            btn.setProperty("active", p == pagina)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        {
            self.PAGE_DASHBOARD:  self._cargar_dashboard,
            self.PAGE_OPERADORES: self._cargar_operadores,
            self.PAGE_USUARIOS:   self._cargar_usuarios,
            self.PAGE_ACTIVIDAD:  self._cargar_actividad,
            self.PAGE_SISTEMA:    self._cargar_sistema,
        }[pagina]()

    def _cargar_dashboard(self):
        todos      = self.dao.obtenerTodosLosUsuarios()
        operadores = [u for u in todos if u.tipo_usuario == "Operador"]
        clientes   = [u for u in todos if u.tipo_usuario == "Cliente"]
        bloqueados = [u for u in todos if u.cuenta_bloqueada]

        self.lblTotalOperadores.setText(str(len(operadores)))
        self.lblTotalClientes.setText(str(len(clientes)))
        self.lblTotalBloqueados.setText(str(len(bloqueados)))
        self.lblTotalUsuarios.setText(str(len(todos)))

        self._poblar_tabla_actividad(self.tablaDashActividad, max_filas=8)

    def _cargar_operadores(self):
        todos = self.dao.obtenerTodosLosUsuarios()
        self._operadores_cache = [u for u in todos if u.tipo_usuario == "Operador"]
        self._poblar_tabla_operadores(self._operadores_cache)

    def _poblar_tabla_operadores(self, usuarios):
        tabla = self.tablaOperadores
        tabla.setRowCount(0)
        for u in usuarios:
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(str(u.usuario_id), center=True))
            tabla.setItem(row, 1, self._item(u.nombre_completo or ""))
            tabla.setItem(row, 2, self._item(u.dni_nie or ""))
            tabla.setItem(row, 3, self._item(u.email or ""))
            tabla.setItem(row, 4, self._item(u.telefono or "—"))
            fecha = str(u.fecha_registro)[:10] if u.fecha_registro else "—"
            tabla.setItem(row, 6, self._item(fecha, center=True))
            tabla.setCellWidget(row, 5, self._badge_estado(u.estado, u.cuenta_bloqueada))
            tabla.setCellWidget(row, 7, self._acciones_operador(u))

    def _filtrar_operadores(self):
        txt    = self.searchOperadores.text().strip().lower()
        estado = self.filtroEstadoOp.currentText()
        cache  = getattr(self, "_operadores_cache", [])
        filtrados = [
            u for u in cache
            if (txt in (u.nombre_completo or "").lower()
                or txt in (u.email or "").lower()
                or txt in (u.dni_nie or "").lower())
            and (estado == "Todos los estados"
                 or (estado == "Bloqueado" and u.cuenta_bloqueada)
                 or (estado != "Bloqueado" and u.estado == estado and not u.cuenta_bloqueada))
        ]
        self._poblar_tabla_operadores(filtrados)

    def _nuevo_operador(self):
        dlg = DialogoOperador(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        datos = dlg.datos()
        if not all([datos["dni_nie"], datos["nombre_completo"], datos["email"], datos["password"]]):
            QMessageBox.warning(self, "Campos incompletos", "Rellena todos los campos obligatorios.")
            return
        exito, msg = self.logica.registrarUsuario(
            datos["dni_nie"], datos["nombre_completo"],
            datos["email"], datos["telefono"], datos["password"]
        )
        if exito:
            self._registrar_accion("Creación", f"Nuevo operador: {datos['email']}")
            QMessageBox.information(self, "Operador creado", msg)
            self._cargar_operadores()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _editar_operador(self, usuario):
        dlg = DialogoOperador(self, usuario)
        if dlg.exec_() != QDialog.Accepted:
            return
        datos = dlg.datos()
        if datos["password"]:
            self.dao.actualizarContrasena(usuario.usuario_id, datos["password"])
        self._registrar_accion("Modificación", f"Operador editado: {usuario.email}")
        QMessageBox.information(self, "Actualizado", "Datos del operador actualizados.")
        self._cargar_operadores()

    def _toggle_bloqueo(self, usuario):
        if usuario.cuenta_bloqueada:
            self.dao.desbloquearCuenta(usuario.usuario_id)
            self._registrar_accion("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")
            QMessageBox.information(self, "Desbloqueada", f"Cuenta de {usuario.nombre_completo} desbloqueada.")
        else:
            self.dao.bloquearCuenta(usuario.usuario_id)
            self._registrar_accion("Bloqueo", f"Cuenta bloqueada: {usuario.email}")
            QMessageBox.warning(self, "Bloqueada", f"Cuenta de {usuario.nombre_completo} bloqueada.")
        self._cargar_operadores()

    def _exportar_operadores(self):
        try:
            from PyQt5.QtWidgets import QFileDialog
            ruta, _ = QFileDialog.getSaveFileName(
                self, "Exportar operadores", "operadores.csv", "CSV (*.csv)"
            )
            if not ruta:
                return
            cache = getattr(self, "_operadores_cache", [])
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("ID,Nombre,DNI,Email,Telefono,Estado,Fecha\n")
                for u in cache:
                    estado = "Bloqueado" if u.cuenta_bloqueada else u.estado
                    f.write(f"{u.usuario_id},{u.nombre_completo},{u.dni_nie},{u.email},"
                            f"{u.telefono or ''},{estado},{u.fecha_registro or ''}\n")
            QMessageBox.information(self, "Exportado", f"Guardado en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    def _cargar_usuarios(self):
        self._usuarios_cache = self.dao.obtenerTodosLosUsuarios()
        self._poblar_tabla_usuarios(self._usuarios_cache)

    def _poblar_tabla_usuarios(self, usuarios):
        tabla = self.tablaUsuarios
        tabla.setRowCount(0)
        for u in usuarios:
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(str(u.usuario_id), center=True))
            tabla.setItem(row, 1, self._item(u.nombre_completo or ""))
            tabla.setItem(row, 2, self._item(u.dni_nie or ""))
            tabla.setItem(row, 3, self._item(u.email or ""))
            tabla.setItem(row, 4, self._item(u.tipo_usuario or ""))
            fecha = str(u.fecha_registro)[:10] if u.fecha_registro else "—"
            tabla.setItem(row, 6, self._item(fecha, center=True))
            tabla.setCellWidget(row, 5, self._badge_estado(u.estado, u.cuenta_bloqueada))
            tabla.setCellWidget(row, 7, self._acciones_usuario(u))

    def _filtrar_usuarios(self):
        txt    = self.searchUsuarios.text().strip().lower()
        tipo   = self.filtroTipoUs.currentText()
        estado = self.filtroEstadoUs.currentText()
        cache  = getattr(self, "_usuarios_cache", [])
        filtrados = [
            u for u in cache
            if (txt in (u.nombre_completo or "").lower()
                or txt in (u.email or "").lower()
                or txt in (u.dni_nie or "").lower())
            and (tipo == "Todos los tipos" or u.tipo_usuario == tipo)
            and (estado == "Todos los estados"
                 or (estado == "Bloqueado" and u.cuenta_bloqueada)
                 or (estado != "Bloqueado" and u.estado == estado and not u.cuenta_bloqueada))
        ]
        self._poblar_tabla_usuarios(filtrados)

    def _cargar_actividad(self):
        self._poblar_tabla_actividad(self.tablaActividad)

    def _poblar_tabla_actividad(self, tabla, max_filas=None):
        tabla.setRowCount(0)
        log = self._backup_log[:]
        if max_filas:
            log = log[-max_filas:]
        for entrada in reversed(log):
            row = tabla.rowCount()
            tabla.insertRow(row)
            if tabla == self.tablaDashActividad:
                tabla.setItem(row, 0, self._item(entrada.get("fecha", ""), center=True))
                tabla.setItem(row, 1, self._item(entrada.get("usuario", "")))
                tabla.setItem(row, 2, self._item(entrada.get("tipo", "")))
                tabla.setItem(row, 3, self._item(entrada.get("detalle", "")))
            else:
                partes = entrada.get("fecha", " ").split(" ")
                tabla.setItem(row, 0, self._item(partes[0] if partes else "", center=True))
                tabla.setItem(row, 1, self._item(partes[1] if len(partes) > 1 else "", center=True))
                tabla.setItem(row, 2, self._item(self.usuario_actual.nombre_completo or ""))
                tabla.setItem(row, 3, self._item(self.usuario_actual.tipo_usuario or ""))
                tabla.setItem(row, 4, self._item(entrada.get("tipo", "")))
                tabla.setItem(row, 5, self._item(entrada.get("detalle", "")))
                tabla.setItem(row, 6, self._item("127.0.0.1", center=True))

    def _filtrar_actividad(self):
        self._cargar_actividad()

    def _registrar_accion(self, tipo, detalle):
        self._backup_log.append({
            "fecha":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": self.usuario_actual.nombre_completo or "Admin",
            "tipo":    tipo,
            "detalle": detalle,
        })

    def _cargar_sistema(self):
        self._poblar_tabla_backups()

    def _hacer_backup(self):
        ahora          = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"softrip_backup_{ahora}.bak"
        try:
            entrada = {
                "fecha":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "archivo": nombre_archivo,
                "tamano":  "—",
                "estado":  "OK",
            }
            self._backup_log.append({
                "fecha":   entrada["fecha"],
                "usuario": self.usuario_actual.nombre_completo or "Admin",
                "tipo":    "Backup",
                "detalle": f"Backup generado: {nombre_archivo}",
            })
            self._backup_registros = getattr(self, "_backup_registros", [])
            self._backup_registros.append(entrada)
            self.bkLast1.setText(f"Último backup: {entrada['fecha']}")
            self._poblar_tabla_backups()
            QMessageBox.information(
                self, "Backup completado",
                f"Copia de seguridad generada.\nArchivo: {nombre_archivo}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error en backup", str(e))

    def _poblar_tabla_backups(self):
        tabla     = self.tablaBackups
        tabla.setRowCount(0)
        registros = getattr(self, "_backup_registros", [])
        for r in reversed(registros):
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(r["fecha"], center=True))
            tabla.setItem(row, 1, self._item(r["archivo"]))
            tabla.setItem(row, 2, self._item(r["tamano"], center=True))
            tabla.setItem(row, 3, self._item(r["estado"], center=True))
            btn = QPushButton("Descargar")
            btn.setObjectName("btnSecondary")
            btn.setCursor(Qt.PointingHandCursor)
            tabla.setCellWidget(row, 4, self._wrap_widget(btn))

    def _item(self, texto, center=False):
        item = QTableWidgetItem(str(texto))
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def _badge_estado(self, estado, bloqueada=False):
        if bloqueada:
            texto, (bg, fg) = "Bloqueado", self.ESTADO_COLORES["Bloqueado"]
        else:
            texto = estado or "Desconocido"
            bg, fg = self.ESTADO_COLORES.get(texto, ("#EEEEEE", "#555555"))
        lbl = QLabel(f"  {texto}  ")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background-color:{bg}; color:{fg};"
            "border-radius:8px; font-size:10px; font-weight:bold; padding:2px 0px;"
        )
        return self._wrap_widget(lbl)

    def _acciones_operador(self, usuario):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)

        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("btnEdit")
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.clicked.connect(lambda _, u=usuario: self._editar_operador(u))

        etiqueta     = "Desbloquear" if usuario.cuenta_bloqueada else "Bloquear"
        btn_bloquear = QPushButton(etiqueta)
        btn_bloquear.setObjectName("btnSuccess" if usuario.cuenta_bloqueada else "btnDanger")
        btn_bloquear.setCursor(Qt.PointingHandCursor)
        btn_bloquear.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo(u))

        lay.addWidget(btn_editar)
        lay.addWidget(btn_bloquear)
        lay.addStretch()
        return contenedor

    def _acciones_usuario(self, usuario):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)

        etiqueta = "Desbloquear" if usuario.cuenta_bloqueada else "Bloquear"
        btn = QPushButton(etiqueta)
        btn.setObjectName("btnSuccess" if usuario.cuenta_bloqueada else "btnDanger")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo_usuario(u))

        lay.addWidget(btn)
        lay.addStretch()
        return contenedor

    def _toggle_bloqueo_usuario(self, usuario):
        if usuario.cuenta_bloqueada:
            self.dao.desbloquearCuenta(usuario.usuario_id)
            self._registrar_accion("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")
        else:
            self.dao.bloquearCuenta(usuario.usuario_id)
            self._registrar_accion("Bloqueo", f"Cuenta bloqueada: {usuario.email}")
        self._cargar_usuarios()

    def _wrap_widget(self, widget):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(widget)
        return contenedor

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Seguro que quieres cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            from src.vista.Login import MiVentana
            self.ventana_login = MiVentana()
            self.ventana_login.show()
            self.close()


if __name__ == "__main__":
    from src.modelo.vo.UsuariosVO import UsuarioVO
    app = QApplication(sys.argv)
    usuario_prueba = UsuarioVO(1, "12345678A", "Admin Softrip", "admin@softrip.es",
                               "600000000", "Administrador", "Activo", False)
    ventana = VentanaAdmin(usuario_prueba)
    ventana.show()
    sys.exit(app.exec_())
