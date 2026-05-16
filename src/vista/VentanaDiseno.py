import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaDiseno.ui"
)


class VentanaDiseno(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)

        self.user = user

        self._conectar_senales()

    def _conectar_senales(self):
        self.btnNuevoPaquete.clicked.connect(self._nuevo_paquete)
        self.btnGuardar.clicked.connect(self._guardar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    def _nuevo_paquete(self):
        self._limpiar_formulario()

    def _guardar_paquete(self):
        nombre      = self.inputNombre.text().strip()
        destino     = self.inputDestino.text().strip()
        duracion    = self.inputDuracion.text().strip()
        precio      = self.inputPrecio.text().strip()
        descripcion = self.textDescripcion.toPlainText().strip()

        if not nombre or not destino:
            self.lblEstado.setText("Por favor rellena al menos Nombre y Destino.")
            self.lblEstado.setStyleSheet("color: #e05252;")
            return

        # Aqui llamarias al controlador/modelo real
        self.lblEstado.setText(f"Paquete '{nombre}' guardado correctamente.")
        self.lblEstado.setStyleSheet("color: #5e8d8d;")

    def _limpiar_formulario(self):
        self.inputNombre.clear()
        self.inputDestino.clear()
        self.inputDuracion.clear()
        self.inputPrecio.clear()
        self.textDescripcion.clear()
        self.lblEstado.clear()
