from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import sys

Form, Window = uic.loadUiType("./src/vista/ui/vistaCliente.ui")

class VentanaCliente(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self._connect_signals()

    def _connect_signals(self):
        self.btnCuenta.clicked.connect(self._abrir_cuenta)
        # Buscador
        self.btnBuscar.clicked.connect(self._buscar_paquetes)
        # Tarjetas destacadas
        self.card1_btn.clicked.connect(lambda: self._ver_paquete(1))
        self.card2_btn.clicked.connect(lambda: self._ver_paquete(2))
        self.card3_btn.clicked.connect(lambda: self._ver_paquete(3))

    def _abrir_cuenta(self):
        """Abre el panel / ventana de la cuenta del usuario."""
        QMessageBox.information(self, "Mi cuenta", "Aquí irá la vista de cuenta del usuario.")

    def _buscar_paquetes(self):
        """Recoge los filtros del buscador y lanza la búsqueda."""
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
                self,
                "Fechas incorrectas",
                "La fecha de vuelta no puede ser anterior a la de ida."
            )
            return

        # TODO: llamar al controlador / servicio de búsqueda con estos parámetros
        print(
            f"Buscando: destino={destino!r}, ida={fecha_ida.toString('dd/MM/yyyy')}, "
            f"vuelta={fecha_vuelta.toString('dd/MM/yyyy')}, personas={personas}"
        )

    def _ver_paquete(self, numero: int):
        """Abre el detalle del paquete destacado seleccionado."""
        # TODO: instanciar y mostrar la vista de detalle pasando el id/número de paquete
        QMessageBox.information(
            self,
            "Ver paquete",
            f"Abriendo detalle del paquete {numero}…"
        )
