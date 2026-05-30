"""
VentanaActividad_admin.py  –  Vista del Registro de Actividad
=============================================================
Responsabilidad: pedir los registros al Controlador y pintarlos.
No contiene lógica de negocio.
"""

from PyQt5.QtWidgets import QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistaactividadadmin.ui")


class VentanaActividad_admin(VentanaBase, Form):

    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._ctrl = controlador

        self._configurar_tabla()
        self.filtroAccion.currentTextChanged.connect(self.cargar)

    # ── Configuración inicial ─────────────────────────────────────────────────

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

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar(self):
        """Llamado por el Controlador cada vez que se navega a esta página."""
        tipo      = self.filtroAccion.currentText()
        registros = self._ctrl.obtener_actividad(tipo_accion=tipo)
        tabla     = self.tablaActividad
        tabla.setRowCount(0)

        for r in registros:
            row = tabla.rowCount()
            tabla.insertRow(row)
            # Separamos fecha y hora para mostrarlas en columnas distintas
            fecha_str = str(r.fecha) if r.fecha else ""
            partes    = fecha_str.split(" ")
            tabla.setItem(row, 0, self._item(partes[0] if partes else "",               center=True))
            tabla.setItem(row, 1, self._item(partes[1][:8] if len(partes) > 1 else "",  center=True))
            tabla.setItem(row, 2, self._item(r.nombre_usuario or ""))
            tabla.setItem(row, 3, self._item(r.tipo_usuario  or ""))
            tabla.setItem(row, 4, self._item(r.tipo_accion   or ""))
            tabla.setItem(row, 5, self._item(r.detalle       or ""))
            tabla.setItem(row, 6, self._item(r.ip or "127.0.0.1",                       center=True))
