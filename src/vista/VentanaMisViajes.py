import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QSizePolicy
from PyQt5 import uic
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaMisViajes.ui")

_UI_DIR = os.path.join(os.path.dirname(__file__), "ui")


class VentanaMisViajes(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_viajes = self
        self._cargar_datos()
        self._connect_signals()
        self._cargar_viajes()

    def _cargar_datos(self):
        self.userNameLabel.setText(self.user.nombre_completo.split()[0])
        self.avatarLabel.setText(self.user.nombre_completo[0].upper())

    def _connect_signals(self):
        self.logoBtn.clicked.connect(self.controlador.volver_a_principal)
        self.btnNavAjustes.clicked.connect(self.controlador.ir_a_ajustes)
        self.btnLogout.clicked.connect(self._cerrar_sesion)

    # ── Carga de viajes ───────────────────────────────────────────────────────

    def _cargar_viajes(self):
        while self.listaViajes.count():
            item = self.listaViajes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        viajes = self.controlador.obtener_viajes_cliente()

        if not viajes:
            self.placeholderIcon.show()
            self.placeholderLabel.show()
            self.placeholderSub.show()
            self.scrollViajes.hide()
            return

        self.placeholderIcon.hide()
        self.placeholderLabel.hide()
        self.placeholderSub.hide()
        self.scrollViajes.show()

        for viaje in viajes:
            card = self._crear_tarjeta(viaje)
            self.listaViajes.addWidget(card)

        self.scrollContent.adjustSize()
        self.scrollViajes.updateGeometry()

    def _crear_tarjeta(self, viaje: dict) -> QWidget:
        contenedor = QWidget()
        uic.loadUi(os.path.join(_UI_DIR, "cardPaqueteViaje.ui"), contenedor)

        duracion = viaje["duracion"]
        sufijo = f"{duracion} noche" if str(duracion) == "1" else f"{duracion} noches"
        contenedor.card_titulo.setText(f"{viaje.get('destino', '')} · {sufijo}")

        descripcion =  viaje["servicios"] if viaje["servicios"] else viaje["descripcion"][:60]
        contenedor.card_desc.setText(descripcion)

        try:
            precio_fmt = f"Desde {float(viaje['monto_total']):.0f} €"
        except (ValueError, TypeError):
            precio_fmt = f"Desde {viaje['monto_total']} €"
        contenedor.card_precio.setText(precio_fmt)

        pid = viaje["paquete_id"]
        contenedor.card_btn.clicked.connect(lambda _checked, p=pid: self.controlador.ver_paquete(p))

        contenedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        contenedor.setFixedHeight(155)
        return contenedor

    # ── Sesión ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.controlador.cerrar_sesion()
