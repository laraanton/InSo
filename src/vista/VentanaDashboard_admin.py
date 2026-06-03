"""
VentanaDashboard_admin.py  –  Vista del Dashboard del Administrador
===================================================================
    - __init__ recibe user= (no controlador)
    - controlador llega por setter, que llama a cargar()
"""

from PyQt5.QtWidgets import QAbstractItemView, QHeaderView
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistadashboardadmin.ui")


class VentanaDashboard_admin(VentanaBase, Form):

    # Señal que VentanaAdmin escucha para saltar a la página de actividad
    ir_a_actividad = pyqtSignal()

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._user = user
        self._ctrl = None

        self._configurar_tabla()
        self.btnVerTodosDash.clicked.connect(self.ir_a_actividad.emit)

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self.cargar()

    # ── Configuración inicial ─────────────────────────────────────────────────

    def _configurar_tabla(self):
        header = self.tablaDashActividad.horizontalHeader()
        anchos = [150, 170, None, None]
        for i, w in enumerate(anchos):
            if w is None:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.tablaDashActividad.setColumnWidth(i, w)
        self.tablaDashActividad.verticalHeader().setDefaultSectionSize(38)
        self.tablaDashActividad.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablaDashActividad.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar(self):
        todos      = self._ctrl.obtener_todos_usuarios()
        operadores = [u for u in todos if u.tipo_usuario == "Operador"]
        clientes   = [u for u in todos if u.tipo_usuario == "Cliente"]
        bloqueados = [u for u in todos if u.cuenta_bloqueada]

        self.lblTotalOperadores.setText(str(len(operadores)))
        self.lblTotalClientes.setText(str(len(clientes)))
        self.lblTotalBloqueados.setText(str(len(bloqueados)))
        self.lblTotalUsuarios.setText(str(len(todos)))

        self._poblar_actividad_reciente()

    def _poblar_actividad_reciente(self):
        tabla = self.tablaDashActividad
        tabla.setRowCount(0)

        registros = self._ctrl.obtener_actividad(limite=8)
        for r in registros:
            row = tabla.rowCount()
            tabla.insertRow(row)
            fecha = str(r.fecha)[:19] if r.fecha else "—"
            tabla.setItem(row, 0, self._item(fecha,                  selectable=False, center=True))
            tabla.setItem(row, 1, self._item(r.nombre_usuario or "", selectable=False))
            tabla.setItem(row, 2, self._item(r.tipo_accion   or "", selectable=False))
            tabla.setItem(row, 3, self._item(r.detalle       or "", selectable=False))
