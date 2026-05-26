from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistadashboardadmin.ui")


class VentanaDashboard_admin(VentanaBase, Form):

    ir_a_actividad = pyqtSignal()

    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.controlador = controlador

        self._configurar_tabla()
        self.btnVerTodosDash.clicked.connect(self.ir_a_actividad.emit)

    def _configurar_tabla(self):
        header = self.tablaDashActividad.horizontalHeader()
        anchos = [130, 160, 100, None]
        for i, w in enumerate(anchos):
            if w is None:
                header.setSectionResizeMode(i, header.Stretch)
            else:
                self.tablaDashActividad.setColumnWidth(i, w)
        self.tablaDashActividad.verticalHeader().setDefaultSectionSize(38)
        self.tablaDashActividad.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablaDashActividad.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def cargar(self):
        todos      = self.controlador.obtener_todos_los_usuarios()
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
        filas = self.controlador.obtener_actividad(limite=8)
        for fila in filas:
            row = tabla.rowCount()
            tabla.insertRow(row)
            fecha = str(fila[1])[:19] if fila[1] else "—"
            tabla.setItem(row, 0, self._item(fecha, center=True, selectable=False))
            tabla.setItem(row, 1, self._item(fila[2] or "",       selectable=False))
            tabla.setItem(row, 2, self._item(fila[4] or "",       selectable=False))
            tabla.setItem(row, 3, self._item(fila[5] or "",       selectable=False))