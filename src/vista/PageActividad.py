from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.vista.SOFTRIP_STYLE import softrip_style
Form, _ = uic.loadUiType("./src/vista/ui/vistaactividadadmin.ui")

class PageDashboard(QWidget, Form):
    def __init__(self, dao, usuario_actual, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setStyleSheet(softrip_style)

class PageActividad(QWidget, Form):

    def __init__(self, dao, usuario_actual, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.dao            = dao
        self.usuario_actual = usuario_actual

        self._configurar_tabla()
        self.filtroAccion.currentTextChanged.connect(self.cargar)

    def _configurar_tabla(self):
       
        anchos = [100, 70, 150, 90, 120, None, 110]
        header = self.tablaActividad.horizontalHeader()
        for i, w in enumerate(anchos):
            if w is None:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                self.tablaActividad.setColumnWidth(i, w)
        self.tablaActividad.verticalHeader().setDefaultSectionSize(38)
        self.tablaActividad.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaActividad.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def cargar(self):
        tipo   = self.filtroAccion.currentText()  # "Todas", "Creación", "Bloqueo"...
        filas  = self.dao.obtenerActividad(tipo_accion=tipo)
        tabla  = self.tablaActividad
        tabla.setRowCount(0)

        for fila in filas:
            row = tabla.rowCount()
            tabla.insertRow(row)
            fecha_str = str(fila[1]) if fila[1] else ""
            partes    = fecha_str.split(" ")
            tabla.setItem(row, 0, self._item(partes[0] if partes else "",          center=True))
            tabla.setItem(row, 1, self._item(partes[1][:8] if len(partes) > 1 else "", center=True))
            tabla.setItem(row, 2, self._item(fila[2] or ""))   # nombre
            tabla.setItem(row, 3, self._item(fila[3] or ""))   # rol
            tabla.setItem(row, 4, self._item(fila[4] or ""))   # tipo_accion
            tabla.setItem(row, 5, self._item(fila[5] or ""))   # detalle  ← columna Stretch, no se corta
            tabla.setItem(row, 6, self._item(fila[6] or "127.0.0.1", center=True))  # ip

    def _item(self, texto, center=False):
        item = QTableWidgetItem(str(texto))
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item