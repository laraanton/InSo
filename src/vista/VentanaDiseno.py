import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDate


UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaDiseno.ui"
)

AVION = "✈️"

class VentanaDiseno(QWidget):

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value


    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = None
        self._inicializar_fechas()
        self._conectar_senales()

    # Inicialización 

    def _inicializar_fechas(self):
        hoy = QDate.currentDate()
        self.inputFechaIni.setMinimumDate(hoy)
        self.inputFechaFin.setMinimumDate(hoy)
        self.inputFechaIni.setDate(hoy)
        # fecha_fin arranca igual a hoy; se recalcula cuando el usuario
        # escriba los días de duración (señal textChanged ya conectada)
        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(hoy)
        self.inputFechaFin.setReadOnly(True)

    # Señales 

    def _conectar_senales(self):
        self.btnNuevoPaquete.clicked.connect(self._limpiar_formulario)
        self.btnGuardar.clicked.connect(self._guardar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)
        self.inputFechaIni.dateChanged.connect(lambda _: self._actualizar_fecha_fin())
        self.inputDuracion.textChanged.connect(lambda _: self._actualizar_fecha_fin())

    # Acciones 

    def _guardar_paquete(self):
        datos = {
            "nombre":      self.inputNombre.text().strip(),
            "destino":     self.inputDestino.text().strip(),
            "duracion":    self.inputDuracion.text().strip(),
            "precio":      self.inputPrecio.text().strip(),
            "descripcion": self.textDescripcion.toPlainText().strip(),
            "fecha_ini":   self.inputFechaIni.date().toString("yyyy-MM-dd"),
            "fecha_fin":   self.inputFechaFin.date().toString("yyyy-MM-dd"),
            "emoji":       AVION,
            "servicios":   "",
            "perfil":      "",
        }

        resultado = self._ctrl.crear_paquete(datos)
        self._set_estado(resultado.mensaje, error=not resultado.ok)

    def _limpiar_formulario(self):
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio):
            w.clear()
        self.textDescripcion.clear()
        self.lblEstado.clear()
        hoy = QDate.currentDate()
        self.inputFechaIni.setDate(hoy)
        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(hoy)
        self.inputFechaFin.setReadOnly(True)

    # Helpers 

    def _actualizar_fecha_fin(self):
        """Calcula fecha_fin = fecha_ini + duración (días).
        Si la duración no es un número válido, fecha_fin = fecha_ini."""
        fecha_ini = self.inputFechaIni.date()
        try:
            dias = int(self.inputDuracion.text().strip())
            if dias < 0:
                dias = 0
        except ValueError:
            dias = 0

        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setMinimumDate(fecha_ini)
        self.inputFechaFin.setDate(fecha_ini.addDays(dias))
        self.inputFechaFin.setReadOnly(True)

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
