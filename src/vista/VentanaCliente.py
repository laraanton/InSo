from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QDate
from datetime import date

from src.modelo.dao.PaqueteDAO import PaqueteDAO 

Form, Window = uic.loadUiType("./src/vista/ui/vistaCliente.ui")

class VentanaCliente(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.menuCuenta.hide()
        self._connect_signals()
        self._cargar_paquetes_destacados()
        
        hoy = QDate.currentDate()
        self.in_fecha_ida.setDate(hoy)
        self.in_fecha_vuelta.setDate(hoy.addDays(1))

    def _connect_signals(self):
        self.btnCuenta.clicked.connect(self._abrir_cuenta)
        self.btnAjustes.clicked.connect(self._ir_ajustes)
        self.btnMisViajes.clicked.connect(self._ir_mis_viajes)
        self.btnCerrarSesion.clicked.connect(self._cerrar_sesion)
        self.btnBuscar.clicked.connect(self._buscar_paquetes)
        # Los botones de tarjeta se reconectan en _cargar_paquetes_destacados

    def _cargar_paquetes_destacados(self):
        dao = PaqueteDAO()
        paquetes = dao.obtener_todos()[:6]

        tarjetas = [
            {"card": self.card1, "icono": self.card1_icono, "titulo": self.card1_titulo,
            "desc": self.card1_desc, "precio": self.card1_precio, "btn": self.card1_btn},
            {"card": self.card2, "icono": self.card2_icono, "titulo": self.card2_titulo,
            "desc": self.card2_desc, "precio": self.card2_precio, "btn": self.card2_btn},
            {"card": self.card3, "icono": self.card3_icono, "titulo": self.card3_titulo,
            "desc": self.card3_desc, "precio": self.card3_precio, "btn": self.card3_btn},
            {"card": self.card4, "icono": self.card4_icono, "titulo": self.card4_titulo,
            "desc": self.card4_desc, "precio": self.card4_precio, "btn": self.card4_btn},
            {"card": self.card5, "icono": self.card5_icono, "titulo": self.card5_titulo,
            "desc": self.card5_desc, "precio": self.card5_precio, "btn": self.card5_btn},
            {"card": self.card6, "icono": self.card6_icono, "titulo": self.card6_titulo,
            "desc": self.card6_desc, "precio": self.card6_precio, "btn": self.card6_btn},
        ]

        self._ids_destacados = []

        for i, tarjeta in enumerate(tarjetas):
            if i < len(paquetes):
                p = paquetes[i]
                self._ids_destacados.append(p["id"])

                tarjeta["icono"].setText("✈️")

                duracion = p["duracion"]
                sufijo   = f"{duracion} noche" if duracion == "1" else f"{duracion} noches"
                tarjeta["titulo"].setText(f"{p['destino']} · {sufijo}")

                descripcion = p["servicios"] if p["servicios"] else p["descripcion"][:32]
                tarjeta["desc"].setText(descripcion)

                try:
                    precio_fmt = f"Desde {float(p['precio']):.0f} €"
                except ValueError:
                    precio_fmt = f"Desde {p['precio']} €"
                tarjeta["precio"].setText(precio_fmt)

                tarjeta["card"].show()
            else:
                self._ids_destacados.append(None)
                tarjeta["card"].hide()

        # Reconectar botones con IDs reales
        botones = [self.card1_btn, self.card2_btn, self.card3_btn,
                self.card4_btn, self.card5_btn, self.card6_btn]
        for btn in botones:
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass

        for i, btn in enumerate(botones):
            pid = self._ids_destacados[i]
            btn.clicked.connect(lambda _checked, p=pid: self._ver_paquete(p))

    # ── Resto de métodos (sin cambios) ─────────────────────────────────────

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
        elif fecha_ida < date.today():
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
        """Abre el detalle del paquete. Si el id es None la tarjeta estaba vacía."""
        if paquete_id is None:
            return
        from src.controlador.ControladorCliente import ControladorCliente
        from src.vista.VentanaDetallePaquete import VentanaDetallePaquete

        controlador = ControladorCliente(self.user)
        paquete = PaqueteDAO().obtener_por_id(paquete_id)
        self.ventana_detalle = VentanaDetallePaquete(self.user, paquete, controlador)

        self.ventana_detalle.show()
        self.hide()

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Si | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Si:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
