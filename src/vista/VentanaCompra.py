"""
VentanaCompra.py  Vista de Gestión de Compra / Reservas (Req_25, Req_26)
============================================================================
Responsabilidad: mostrar reservas, filtrarlas, cambiar su estado y exportar.
Toda la lógica de datos pasa por ControladorOperador.

Widgets del .ui que usa esta vista:
    tablaReservas (QTableWidget, 7 columnas),
    inputBuscar, comboEstado, lblEstado,
    btnNuevaReserva, btnExportar
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.controlador.ControladorOperador import ControladorOperador

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaCompra.ui"
)

# Estados válidos según Req_26 / sección 2.2.3 ERS
ESTADOS = [
    "Pendiente confirmacion",
    "Confirmado",
    "Pagado",
    "En curso",
    "Finalizado",
    "Cancelado",
    "Reembolsado",
]

# Colores de badge por estado (Req_6)
_COLOR_ESTADO = {
    "Pendiente confirmacion": ("#fff3cd", "#856404"),
    "Confirmado":             ("#d4edda", "#155724"),
    "Pagado":                 ("#d1ecf1", "#0c5460"),
    "En curso":               ("#cce5ff", "#004085"),
    "Finalizado":             ("#e8f2f2", "#2d6b6b"),
    "Cancelado":              ("#f8d7da", "#721c24"),
    "Reembolsado":            ("#e2e3e5", "#383d41"),
}

COL_ID, COL_CLIENTE, COL_PAQUETE, COL_FECHA, COL_PRECIO, COL_ESTADO, COL_ACCIONES = range(7)


class VentanaCompra(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = ControladorOperador()

        self._configurar_tabla()
        self._conectar_senales()
        self.refrescar()          # carga inicial

    # ── Configuración ──────────────────────────────────────────────────────

    def _configurar_tabla(self):
        t = self.tablaReservas
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setVisible(False)
        t.setColumnWidth(COL_ID,      100)
        t.setColumnWidth(COL_CLIENTE, 150)
        t.setColumnWidth(COL_PAQUETE, 160)
        t.setColumnWidth(COL_FECHA,   110)
        t.setColumnWidth(COL_PRECIO,   90)
        t.setColumnWidth(COL_ESTADO,  130)

    def _conectar_senales(self):
        self.btnNuevaReserva.clicked.connect(self._nueva_reserva)
        self.btnExportar.clicked.connect(self._exportar_csv)
        self.inputBuscar.textChanged.connect(self._filtrar)
        self.comboEstado.currentIndexChanged.connect(self._filtrar)

    # ── Carga / filtrado ───────────────────────────────────────────────────

    def refrescar(self):
        """Recarga la tabla completa desde el controlador."""
        self._filtrar()

    def _filtrar(self):
        """Filtra reservas según búsqueda y estado, y repinta la tabla."""
        texto  = self.inputBuscar.text().strip()
        estado = self.comboEstado.currentText()
        reservas = self._ctrl.buscar_reservas(texto=texto, estado=estado)
        self._poblar_tabla(reservas)

    # ── Tabla ──────────────────────────────────────────────────────────────

    def _poblar_tabla(self, reservas: list[dict]):
        t = self.tablaReservas
        t.setRowCount(0)

        for fila, r in enumerate(reservas):
            t.insertRow(fila)

            for col, clave in enumerate(["id", "cliente", "paquete", "fecha", "precio"]):
                item = QTableWidgetItem(str(r.get(clave, "")))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                t.setItem(fila, col, item)

            # Badge de estado con color (Req_6)
            estado = r.get("estado", "")
            item_e = QTableWidgetItem(estado)
            item_e.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_e.setTextAlignment(Qt.AlignCenter)
            bg, fg = _COLOR_ESTADO.get(estado, ("#ffffff", "#333333"))
            item_e.setBackground(QColor(bg))
            item_e.setForeground(QColor(fg))
            t.setItem(fila, COL_ESTADO, item_e)

            self._insertar_combo_estado(t, fila, r["id"], estado)

        t.resizeRowsToContents()

    def _insertar_combo_estado(self, tabla, fila: int, id_pedido: str, estado_actual: str):
        """Inserta el combo desplegable de cambio de estado en la columna Acciones."""
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(4, 2, 4, 2)

        combo = QComboBox()
        combo.addItems(ESTADOS)
        if estado_actual in ESTADOS:
            combo.setCurrentIndex(ESTADOS.index(estado_actual))
        combo.setFixedWidth(170)

        combo.currentTextChanged.connect(
            lambda nuevo, pid=id_pedido, f=fila: self._cambiar_estado(pid, nuevo, f)
        )

        lay.addWidget(combo)
        tabla.setCellWidget(fila, COL_ACCIONES, w)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _cambiar_estado(self, id_pedido: str, nuevo_estado: str, fila: int):
        """Delega el cambio de estado en el controlador (Req_26) y actualiza el badge."""
        ok, msg = self._ctrl.cambiar_estado_reserva(id_pedido, nuevo_estado)
        self._set_estado(msg, error=not ok)
        if ok:
            # Actualizar el badge sin repintar toda la tabla
            item = self.tablaReservas.item(fila, COL_ESTADO)
            if item:
                item.setText(nuevo_estado)
                bg, fg = _COLOR_ESTADO.get(nuevo_estado, ("#ffffff", "#333333"))
                item.setBackground(QColor(bg))
                item.setForeground(QColor(fg))

    def _nueva_reserva(self):
        """
        Punto de entrada para crear una reserva nueva (Req_25).
        Aquí se abriría un diálogo; por ahora inserta un ejemplo.
        Sustituir por: dialogo = DialogoNuevaReserva(self); dialogo.exec_()
        """
        datos = {
            "cliente": "Cliente Ejemplo",
            "paquete": "Escapada Paris",
            "precio":  "1.200 EUR",
        }
        ok, msg = self._ctrl.registrar_reserva(datos)
        self._set_estado(msg, error=not ok)
        if ok:
            self.refrescar()

    def _exportar_csv(self):
        """Exporta las reservas a CSV (Req_19)."""
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar reservas", "reservas.csv", "CSV (*.csv)"
        )
        if not ruta:
            return
        ok, msg = self._ctrl.exportar_csv(ruta)
        self._set_estado(msg, error=not ok)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
