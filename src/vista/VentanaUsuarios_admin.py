"""
VentanaUsuarios_admin.py  –  Vista de Todos los Usuarios
========================================================
Responsabilidad: mostrar la lista de todos los usuarios y
delegar las acciones de bloqueo en el Controlador.
No contiene lógica de negocio.
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistausuariosadmin.ui")


class VentanaUsuarios_admin(VentanaBase, Form):

    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._ctrl  = controlador
        self._cache = []

        self._configurar_tabla()
        self._conectar_senales()

    # ── Configuración inicial ─────────────────────────────────────────────────

    def _configurar_tabla(self):
        # [ID, Nombre, DNI, Email, Tipo, Estado, Registro, Acción]
        # None = Stretch (la columna ocupa el espacio restante)
        anchos = [50, 170, 110, 190, 100, 90, 110, None]
        header = self.tablaUsuarios.horizontalHeader()
        for i, w in enumerate(anchos):
            if w is None:
                header.setSectionResizeMode(i, header.Stretch)
            else:
                header.setSectionResizeMode(i, header.Fixed)
                self.tablaUsuarios.setColumnWidth(i, w)
        self.tablaUsuarios.verticalHeader().setDefaultSectionSize(38)
        self.tablaUsuarios.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaUsuarios.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _conectar_senales(self):
        self.searchUsuarios.textChanged.connect(self._filtrar)
        self.filtroTipoUs.currentTextChanged.connect(self._filtrar)
        self.filtroEstadoUs.currentTextChanged.connect(self._filtrar)

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar(self):
        """Llamado por el Controlador cada vez que se navega a esta página."""
        self._cache = self._ctrl.obtener_todos_usuarios()
        self._poblar(self._cache)

    def _poblar(self, lista):
        tabla = self.tablaUsuarios
        tabla.setRowCount(0)
        for u in lista:
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
            tabla.setCellWidget(row, 7, self._acciones(u))

    # ── Filtro ────────────────────────────────────────────────────────────────

    def _filtrar(self):
        txt    = self.searchUsuarios.text().strip().lower()
        tipo   = self.filtroTipoUs.currentText()
        estado = self.filtroEstadoUs.currentText()
        filtrados = [
            u for u in self._cache
            if (txt in (u.nombre_completo or "").lower()
                or txt in (u.email or "").lower()
                or txt in (u.dni_nie or "").lower())
            and (tipo == "Todos los tipos" or u.tipo_usuario == tipo)
            and (estado == "Todos los estados"
                 or (estado == "Bloqueado" and u.cuenta_bloqueada)
                 or (estado != "Bloqueado" and u.estado == estado and not u.cuenta_bloqueada))
        ]
        self._poblar(filtrados)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _toggle_bloqueo(self, usuario):
        if usuario.cuenta_bloqueada:
            resultado = self._ctrl.desbloquear_cuenta(usuario)
        else:
            resultado = self._ctrl.bloquear_cuenta(usuario)

        if resultado.ok:
            QMessageBox.information(self, "Estado actualizado", resultado.mensaje)
        else:
            QMessageBox.warning(self, "Error", resultado.mensaje)
        self.cargar()

    # ── Widgets de celda ──────────────────────────────────────────────────────

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
        return self._wrap(lbl)

    def _acciones(self, usuario):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)
        etiqueta = "Desbloquear" if usuario.cuenta_bloqueada else "Bloquear"
        btn = QPushButton(etiqueta)
        btn.setObjectName("btnSuccess" if usuario.cuenta_bloqueada else "btnDanger")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo(u))
        lay.addWidget(btn)
        lay.addStretch()
        return contenedor
