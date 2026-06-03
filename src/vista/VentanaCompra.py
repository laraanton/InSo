import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QFileDialog,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox 
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaCompra.ui"
)

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
    "Confirmado": ("#d4edda", "#155724"),
    "Pagado": ("#d1ecf1", "#0c5460"),
    "En curso": ("#cce5ff", "#004085"),
    "Finalizado": ("#e8f2f2", "#2d6b6b"),
    "Cancelado": ("#f8d7da", "#721c24"),
    "Reembolsado": ("#e2e3e5", "#383d41"),
}

COL_ID, COL_CLIENTE, COL_PAQUETE, COL_FECHA, COL_PRECIO, COL_ESTADO, COL_ACCIONES = range(7)


class VentanaCompra(QWidget):

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self.refrescar()


    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        #Se pasa usuario_id al controlador si el user está disponible
        usuario_id = getattr(user, "usuario_id", None) if user else None
        self._ctrl = None
        self._configurar_tabla()
        self._conectar_senales()

    # ── Configuración ──────────────────────────────────────────────────────

    def _configurar_tabla(self):
        t = self.tablaReservas
        t.horizontalHeader().setStretchLastSection(True)
        t.verticalHeader().setVisible(False)
        t.setColumnWidth(COL_ID, 100)
        t.setColumnWidth(COL_CLIENTE, 150)
        t.setColumnWidth(COL_PAQUETE, 160)
        t.setColumnWidth(COL_FECHA, 110)
        t.setColumnWidth(COL_PRECIO, 90)
        t.setColumnWidth(COL_ESTADO, 130)

    def _conectar_senales(self):
        self.btnNuevaReserva.clicked.connect(self._nueva_reserva)
        self.btnExportar.clicked.connect(self._exportar_csv)
        self.inputBuscar.textChanged.connect(self._filtrar)
        self.comboEstado.currentIndexChanged.connect(self._filtrar)

    # ── Carga / filtrado ───────────────────────────────────────────────────

    def refrescar(self):
        self._filtrar()

    def _filtrar(self):
        texto  = self.inputBuscar.text().strip()
        estado = self.comboEstado.currentText()
        # [FIX-2] "Todos los estados" (u opción vacía) no debe filtrarse por estado.
        if estado in ("", "Todos los estados"):
            estado = ""
        reservas = self._ctrl.buscar_reservas(texto=texto, estado=estado)
        self._poblar_tabla(reservas)

    # ── Tabla ──────────────────────────────────────────────────────────────

    def _poblar_tabla(self, reservas: list):
        t = self.tablaReservas
        t.setRowCount(0)

        for fila, r in enumerate(reservas):
            t.insertRow(fila)
            # atributos del VO
            valores_col = [
                getattr(r, "identificador_unico", "") or "", # COL_ID
                getattr(r, "cliente", "") or "", # COL_CLIENTE
                getattr(r, "paquete", "") or "", # COL_PAQUETE
                getattr(r, "fecha", "") or "", # COL_FECHA
                # precio: ReservaVO guarda float en .precio; se formatea para display
                (r.precio_fmt() if callable(getattr(r, "precio_fmt", None)) # se usa precio_fmt() si existe
                 else str(getattr(r, "precio", ""))), # COL_PRECIO
            ]
            for col, valor in enumerate(valores_col):
                item = QTableWidgetItem(str(valor))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                t.setItem(fila, col, item)

            estado = getattr(r, "estado", "") or ""
            item_e = QTableWidgetItem(estado)
            item_e.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_e.setTextAlignment(Qt.AlignCenter)
            bg, fg = _COLOR_ESTADO.get(estado, ("#ffffff", "#333333"))
            item_e.setBackground(QColor(bg))
            item_e.setForeground(QColor(fg))
            t.setItem(fila, COL_ESTADO, item_e)

            # .identificador_unico como clave para cambiar estado
            self._insertar_combo_estado(
                t, fila,
                getattr(r, "identificador_unico", None) or getattr(r, "id", ""),
                estado,
            )

        t.resizeRowsToContents()

    def _insertar_combo_estado(self, tabla, fila: int, id_pedido, estado_actual: str):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(4, 2, 4, 2)

        combo = QComboBox()
        combo.addItems(ESTADOS)
        if estado_actual in ESTADOS:
            combo.setCurrentIndex(ESTADOS.index(estado_actual))
        combo.setFixedWidth(170)
        combo.wheelEvent = lambda event: None

        combo.currentTextChanged.connect(
            lambda nuevo, pid=id_pedido, f=fila: self._cambiar_estado(pid, nuevo, f)
        )

        lay.addWidget(combo)
        tabla.setCellWidget(fila, COL_ACCIONES, w)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _cambiar_estado(self, id_pedido, nuevo_estado: str, fila: int):
        resultado = self._ctrl.cambiar_estado_reserva(id_pedido, nuevo_estado)
       
        self._set_estado(resultado.mensaje, error=not resultado.ok)
        if resultado.ok:
            item = self.tablaReservas.item(fila, COL_ESTADO)
            if item:
                item.setText(nuevo_estado)
                bg, fg = _COLOR_ESTADO.get(nuevo_estado, ("#ffffff", "#333333"))
                item.setBackground(QColor(bg))
                item.setForeground(QColor(fg))
    
    def _nueva_reserva(self):
        # se pide al operador los IDs reales mediante un diálogo antes de llamar al controlador.
        dialogo = _DialogoNuevaReserva(self)
        if dialogo.exec_() != QDialog.Accepted:
            return

        datos = dialogo.datos()
        if not datos:
            return

        resultado = self._ctrl.registrar_reserva(datos)
        self._set_estado(resultado.mensaje, error=not resultado.ok)
        if resultado.ok:
            self.refrescar()

    # función exportar csv con los datos de reservas
    def _exportar_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar reservas", "reservas.csv", "CSV (*.csv)"
        )
        if not ruta:
            return
        resultado = self._ctrl.exportar_csv(ruta)
        self._set_estado(resultado.mensaje, error=not resultado.ok)

    # ── Helpers 

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")


# ── Diálogo auxiliar para nueva reserva ───────────────────────────────────────

class _DialogoNuevaReserva(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva reserva")
        self.setMinimumWidth(320)

        lay = QFormLayout(self)

        self._cliente_id  = QLineEdit()
        self._paquete_id  = QLineEdit()
        self._monto = QLineEdit()
        self._metodo_pago = QLineEdit("PayPal")
        self._fecha_ini   = QLineEdit()   # YYYY-MM-DD  (puede quedar vacío)
        self._fecha_fin   = QLineEdit()

        self._cliente_id.setPlaceholderText("Entero, p.ej. 12")
        self._paquete_id.setPlaceholderText("Entero, p.ej. 3")
        self._monto.setPlaceholderText("Decimal, p.ej. 1200.00")
        self._fecha_ini.setPlaceholderText("YYYY-MM-DD  (opcional)")
        self._fecha_fin.setPlaceholderText("YYYY-MM-DD  (opcional)")

        lay.addRow("ID Cliente *",  self._cliente_id)
        lay.addRow("ID Paquete *",  self._paquete_id)
        lay.addRow("Monto total",   self._monto)
        lay.addRow("Método pago",   self._metodo_pago)
        lay.addRow("Fecha inicio",  self._fecha_ini)
        lay.addRow("Fecha fin",     self._fecha_fin)

        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self,
        )
        botones.accepted.connect(self._validar_y_aceptar)
        botones.rejected.connect(self.reject)
        lay.addRow(botones)

    def _validar_y_aceptar(self):
        errores = []
        if not self._cliente_id.text().strip().isdigit():
            errores.append("• ID Cliente debe ser un número entero.")
        if not self._paquete_id.text().strip().isdigit():
            errores.append("• ID Paquete debe ser un número entero.")
        if errores:
            QMessageBox.warning(self, "Datos inválidos", "\n".join(errores))
            return
        self.accept()

    def datos(self) -> dict | None:
        """Devuelve el dict listo para pasarlo a ControladorOperador.registrar_reserva()."""
        try:
            return {
                "cliente_id":  int(self._cliente_id.text().strip()),
                "paquete_id":  int(self._paquete_id.text().strip()),
                "monto_total": self._monto.text().strip() or "0",
                "metodo_pago": self._metodo_pago.text().strip() or "PayPal",
                "fecha_inicio": self._fecha_ini.text().strip() or None,
                "fecha_fin":    self._fecha_fin.text().strip() or None,
            }
        except (ValueError, AttributeError):
            return None
