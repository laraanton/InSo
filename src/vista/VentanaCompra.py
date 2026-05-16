import os
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaCompra.ui"
)

# Req_26: estados posibles del pedido
ESTADOS = [
    "Pendiente confirmacion",
    "Confirmado",
    "Pagado",
    "En curso",
    "Finalizado",
    "Cancelado",
    "Reembolsado",
]

_COLOR_ESTADO = {
    "Pendiente confirmacion": ("#fff3cd", "#856404"),
    "Confirmado":             ("#d4edda", "#155724"),
    "Pagado":                 ("#d1ecf1", "#0c5460"),
    "En curso":               ("#cce5ff", "#004085"),
    "Finalizado":             ("#e8f2f2", "#2d6b6b"),
    "Cancelado":              ("#f8d7da", "#721c24"),
    "Reembolsado":            ("#e2e3e5", "#383d41"),
}

COL_ID       = 0
COL_CLIENTE  = 1
COL_PAQUETE  = 2
COL_FECHA    = 3
COL_PRECIO   = 4
COL_ESTADO   = 5
COL_ACCIONES = 6


class VentanaCompra(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._datos_completos = []

        self._configurar_tabla()
        self._conectar_senales()
        self.cargar_reservas()

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

    # ── Datos ──────────────────────────────────────────────────────────────

    def cargar_reservas(self):
        """Sustituir por: ControladorCompra().obtener_todas()"""
        self._datos_completos = [
            ("PED-0001", "Ana Garcia",   "Escapada Paris",  "2026-03-10", "1.200 EUR", "Confirmado"),
            ("PED-0002", "Luis Perez",   "Caribe Relax",    "2026-03-11", "2.450 EUR", "Pagado"),
            ("PED-0003", "Marta Lopez",  "Ruta por Italia", "2026-03-12", "980 EUR",   "Pendiente confirmacion"),
            ("PED-0004", "Carlos Ruiz",  "Cancun All Inc.", "2026-03-15", "3.100 EUR", "En curso"),
            ("PED-0005", "Sofia Blanco", "Escapada Paris",  "2026-03-18", "1.200 EUR", "Finalizado"),
            ("PED-0006", "Jorge Martin", "Safari Kenia",    "2026-03-20", "4.800 EUR", "Cancelado"),
            ("PED-0007", "Elena Torres", "Ruta por Italia", "2026-03-22", "980 EUR",   "Reembolsado"),
        ]
        self._poblar_tabla(self._datos_completos)

    def _poblar_tabla(self, datos):
        tabla = self.tablaReservas
        tabla.setRowCount(0)

        for fila, (id_p, cliente, paquete, fecha, precio, estado) in enumerate(datos):
            tabla.insertRow(fila)

            for col, valor in enumerate([id_p, cliente, paquete, fecha, precio]):
                item = QTableWidgetItem(valor)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                tabla.setItem(fila, col, item)

            # Badge estado con color (Req_6)
            item_e = QTableWidgetItem(estado)
            item_e.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_e.setTextAlignment(Qt.AlignCenter)
            bg, fg = _COLOR_ESTADO.get(estado, ("#ffffff", "#333333"))
            item_e.setBackground(QColor(bg))
            item_e.setForeground(QColor(fg))
            tabla.setItem(fila, COL_ESTADO, item_e)

            self._insertar_acciones(tabla, fila, id_p, estado)

        tabla.resizeRowsToContents()

    def _insertar_acciones(self, tabla, fila, id_pedido, estado_actual):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(4, 2, 4, 2)
        combo = QComboBox()
        combo.addItems(ESTADOS)
        if estado_actual in ESTADOS:
            combo.setCurrentIndex(ESTADOS.index(estado_actual))
        combo.setFixedWidth(160)
        combo.currentTextChanged.connect(
            lambda nuevo, r=fila, pid=id_pedido: self._cambiar_estado(r, pid, nuevo)
        )
        lay.addWidget(combo)
        tabla.setCellWidget(fila, COL_ACCIONES, w)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _filtrar(self):
        texto  = self.inputBuscar.text().strip().lower()
        estado = self.comboEstado.currentText()
        filtrados = [
            r for r in self._datos_completos
            if (not texto or any(texto in c.lower() for c in r))
            and (estado == "Todos los estados" or r[5] == estado)
        ]
        self._poblar_tabla(filtrados)

    def _cambiar_estado(self, fila, id_pedido, nuevo_estado):
        """Req_26: actualizar estado. Conectar con ControladorCompra().actualizar_estado()"""
        for i, r in enumerate(self._datos_completos):
            if r[0] == id_pedido:
                self._datos_completos[i] = r[:5] + (nuevo_estado,)
                break
        item = self.tablaReservas.item(fila, COL_ESTADO)
        if item:
            item.setText(nuevo_estado)
            bg, fg = _COLOR_ESTADO.get(nuevo_estado, ("#ffffff", "#333333"))
            item.setBackground(QColor(bg))
            item.setForeground(QColor(fg))
        self.lblEstado.setText(f"Pedido {id_pedido} -> '{nuevo_estado}'")
        self.lblEstado.setStyleSheet("color: #5e8d8d; font-weight: bold;")

    def _nueva_reserva(self):
        """Abrir dialogo de nueva reserva — conectar con dialogo real."""
        self.lblEstado.setText("Conectar con dialogo NuevaReserva.")
        self.lblEstado.setStyleSheet("color: #999999;")

    def _exportar_csv(self):
        """Req_19: exportar ventas a CSV."""
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar", "reservas.csv", "CSV (*.csv)")
        if not ruta:
            return
        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(
                    [["ID Pedido", "Cliente", "Paquete", "Fecha", "Precio", "Estado"]]
                    + list(self._datos_completos)
                )
            self.lblEstado.setText(f"Exportado: {ruta}")
            self.lblEstado.setStyleSheet("color: #5e8d8d; font-weight: bold;")
        except Exception as e:
            self.lblEstado.setText(f"Error: {e}")
            self.lblEstado.setStyleSheet("color: #e05252; font-weight: bold;")
