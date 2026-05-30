import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from src.controlador.ControladorOperador import ControladorOperador

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
        self._ctrl = ControladorOperador()
        self._conectar_senales()

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.btnNuevoPaquete.clicked.connect(self._limpiar_formulario)
        self.btnGuardar.clicked.connect(self._guardar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_paquete(self):
        datos = {
            "nombre":      self.inputNombre.text().strip(),
            "destino":     self.inputDestino.text().strip(),
            "duracion":    self.inputDuracion.text().strip(),
            "precio":      self.inputPrecio.text().strip(),
            "descripcion": self.textDescripcion.toPlainText().strip(),
            "servicios":   "",
            "perfil":      "",
            "fecha_ini":   "",
            "fecha_fin":   "",
        }
        resultado = self._ctrl.crear_paquete(datos)          # devuelve OperacionResultadoVO
        self._set_estado(resultado.mensaje, error=not resultado.ok)

    def _limpiar_formulario(self):
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio):
            w.clear()
        self.textDescripcion.clear()
        self.lblEstado.clear()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
