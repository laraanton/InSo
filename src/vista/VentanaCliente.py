import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QSizePolicy, QWidget
from PyQt5.QtCore import QDate
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaCliente.ui")

_COLS = 3


class VentanaCliente(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_principal = self
        self.menuCuenta.hide()
        self._connect_signals()
        self._cargar_paquetes()

        hoy = QDate.currentDate()
        self.in_fecha_ida.setDate(hoy)
        self.in_fecha_vuelta.setDate(hoy.addDays(1))

    def _cargar_paquetes(self):
        while self.gridPaquetes.count():
            item = self.gridPaquetes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        paquetes = self.controlador.obtener_paquetes()

        for i, p in enumerate(paquetes):
            card = self._crear_tarjeta(p)
            if card is None:
                continue
            # se dividen las tarjetas en 3 por fila
            self.gridPaquetes.addWidget(card, i // 3, i % 3)

        self.scrollContent.adjustSize()
        self.scrollPaquetes.updateGeometry()

    def _crear_tarjeta(self, p: dict):
        contenedor = QWidget()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "ui", "cardPaquete.ui"), contenedor)

        duracion = p["duracion"]
        sufijo = f"{duracion} noche" if str(duracion) == "1" else f"{duracion} noches"
        contenedor.card_titulo.setText(f"{p['destino']} · {sufijo}")

        descripcion = p["servicios"] if p["servicios"] else p["descripcion"][:40]
        contenedor.card_desc.setText(descripcion)

        try:
            precio_fmt = f"Desde {float(p['precio']):.0f} €"
        except (ValueError, TypeError):
            precio_fmt = f"Desde {p['precio']} €"
        contenedor.card_precio.setText(precio_fmt)

        pid = p["id"]
        contenedor.card_btn.clicked.connect(
            lambda _checked, pid=pid: self.controlador.ver_paquete(pid)
        )
        contenedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        contenedor.setFixedHeight(155)
        return contenedor

    def _connect_signals(self):
        self.btnCuenta.clicked.connect(self._abrir_cuenta)
        self.btnAjustes.clicked.connect(self.controlador.ir_a_ajustes)
        self.btnMisViajes.clicked.connect(self.controlador.ir_a_mis_viajes)
        self.btnCerrarSesion.clicked.connect(self._cerrar_sesion)
        self.btnBuscar.clicked.connect(self._buscar_paquetes)

    def _abrir_cuenta(self):
        if self.menuCuenta.isVisible():
            self.menuCuenta.hide()
        else:
            self.menuCuenta.show()
            self.menuCuenta.raise_()

    def _buscar_paquetes(self):
        destino      = self.in_destino.text().strip()
        fecha_ida    = self.in_fecha_ida.date()
        fecha_vuelta = self.in_fecha_vuelta.date()

        if not destino:
            QMessageBox.warning(self, "Campo requerido", "Por favor, escribe un destino.")
            self.in_destino.setFocus()
            return

        if fecha_vuelta < fecha_ida:
            QMessageBox.warning(self, "Fechas incorrectas",
                                "La fecha de vuelta no puede ser anterior a la de ida.")
            return

        resultados = self.controlador.buscar_paquetes(destino)
        self._mostrar_resultados(resultados, destino)

    def _mostrar_resultados(self, paquetes: list, termino: str):
        fecha = self.in_fecha_ida.date()
        n_personas = self.in_personas.value()
        self.controlador.ir_a_resultados(paquetes, termino, fecha, n_personas)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión", "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.controlador.cerrar_sesion()
