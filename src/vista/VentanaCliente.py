from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy
from PyQt5.QtCore import QDate
from datetime import date

from src.modelo.dao.PaqueteDAO import PaqueteDAO

Form, Window = uic.loadUiType("./src/vista/ui/vistaCliente.ui")

_COLS = 3  # tarjetas por fila


class VentanaCliente(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.menuCuenta.hide()
        self._connect_signals()
        self._cargar_paquetes()

        hoy = QDate.currentDate()
        self.in_fecha_ida.setDate(hoy)
        self.in_fecha_vuelta.setDate(hoy.addDays(1))

    # ── Carga de tarjetas ────────────────────────────────────────────────────

    def _cargar_paquetes(self):
        while self.gridPaquetes.count():
            item = self.gridPaquetes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        dao = PaqueteDAO()
        paquetes = dao.obtener_todos()

        for i, p in enumerate(paquetes):
            card = self._crear_tarjeta(p)
            if card is None:
                continue
            fila = i // _COLS
            col  = i % _COLS
            self.gridPaquetes.addWidget(card, fila, col)
            
        self.scrollContent.adjustSize()
        self.scrollPaquetes.updateGeometry()

    def _crear_tarjeta(self, p: dict):
        import os
        from PyQt5.QtWidgets import QWidget
        
        contenedor = QWidget()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "ui", "cardPaquete.ui"), contenedor)

        duracion = p["duracion"]
        sufijo = f"{duracion} noche" if duracion == "1" else f"{duracion} noches"
        contenedor.card_titulo.setText(f"{p['destino']} · {sufijo}")

        descripcion = p["servicios"] if p["servicios"] else p["descripcion"][:40]
        contenedor.card_desc.setText(descripcion)

        try:
            precio_fmt = f"Desde {float(p['precio']):.0f} €"
        except (ValueError, TypeError):
            precio_fmt = f"Desde {p['precio']} €"
        contenedor.card_precio.setText(precio_fmt)

        pid = p["id"]
        contenedor.card_btn.clicked.connect(lambda _checked, p=pid: self._ver_paquete(p))

        contenedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        contenedor.setFixedHeight(155)
        return contenedor

    # ── Señales ──────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.btnCuenta.clicked.connect(self._abrir_cuenta)
        self.btnAjustes.clicked.connect(self._ir_ajustes)
        self.btnMisViajes.clicked.connect(self._ir_mis_viajes)
        self.btnCerrarSesion.clicked.connect(self._cerrar_sesion)
        self.btnBuscar.clicked.connect(self._buscar_paquetes)

    def _abrir_cuenta(self):
        if self.menuCuenta.isVisible():
            self.menuCuenta.hide()
        else:
            self.menuCuenta.show()
            self.menuCuenta.raise_()

    def _ir_ajustes(self):
        self.menuCuenta.hide()
        from src.vista.VentanaAjustesCuenta import VentanaAjustesCuenta
        self.ventana_ajustes = VentanaAjustesCuenta(self.user)
        self.ventana_ajustes.show()
        self.hide()

    def _ir_mis_viajes(self):
        self.menuCuenta.hide()
        from src.vista.VentanaMisViajes import VentanaMisViajes
        self.ventana_viajes = VentanaMisViajes(self.user)
        self.ventana_viajes.show()
        self.hide()

    def _buscar_paquetes(self):
        destino      = self.in_destino.text().strip()
        fecha_ida    = self.in_fecha_ida.date()
        fecha_vuelta = self.in_fecha_vuelta.date()
        personas     = self.in_personas.value()

        if not destino:
            QMessageBox.warning(self, "Campo requerido", "Por favor, escribe un destino.")
            self.in_destino.setFocus()
            return

        if fecha_vuelta < fecha_ida:
            QMessageBox.warning(
                self, "Fechas incorrectas",
                "La fecha de vuelta no puede ser anterior a la de ida."
            )
            return
        elif fecha_ida < QDate.fromString(str(date.today()), "yyyy-MM-dd"):
            QMessageBox.warning(
                self, "Fechas incorrectas",
                "La fecha no puede ser anterior a la fecha de hoy."
            )
            return

        print(
            f"Buscando: destino={destino!r}, ida={fecha_ida.toString('dd/MM/yyyy')}, "
            f"vuelta={fecha_vuelta.toString('dd/MM/yyyy')}, personas={personas}"
        )

    def _ver_paquete(self, paquete_id):
        if paquete_id is None:
            return
        from src.controlador.ControladorCliente import ControladorCliente
        from src.vista.VentanaDetallePaquete import VentanaDetallePaquete

        controlador = ControladorCliente(self.user)
        paquete     = PaqueteDAO().obtener_por_id(paquete_id)
        self.ventana_detalle = VentanaDetallePaquete(self.user, paquete, controlador)
        self.ventana_detalle.show()
        self.hide()

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
