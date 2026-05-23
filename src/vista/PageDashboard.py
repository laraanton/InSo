from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic

Form, _ = uic.loadUiType("./src/vista/ui/vistadashboardadmin.ui")


class PageDashboard(QWidget, Form):

    ir_a_actividad = pyqtSignal()

    def __init__(self, dao, usuario_actual, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.dao            = dao
        self.usuario_actual = usuario_actual

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
        todos      = self.dao.obtenerTodosLosUsuarios()
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
        filas = self.dao.obtenerActividad(limite=8)
        for fila in filas:
            row = tabla.rowCount()
            tabla.insertRow(row)
            fecha = str(fila[1])[:19] if fila[1] else "—"
            tabla.setItem(row, 0, self._item(fecha, center=True))
            tabla.setItem(row, 1, self._item(fila[2] or ""))      
            tabla.setItem(row, 2, self._item(fila[4] or ""))       
            tabla.setItem(row, 3, self._item(fila[5] or ""))       

    def _item(self, texto, center=False):
        item = QTableWidgetItem(str(texto))
        item.setFlags(Qt.ItemIsEnabled)
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item