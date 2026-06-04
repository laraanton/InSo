from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QMessageBox

Form, Window = uic.loadUiType("./src/vista/ui/vistaDetallePaquete.ui")


class VentanaDetalleBuscador(QMainWindow, Form):
    def __init__(self, user, paquete: dict, fecha, n_personas):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.paquete = paquete
        self.fecha = fecha
        self.personas = n_personas
        self._controlador = None

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self._rellenar_datos()
        self._conectar_señales()

    def _rellenar_datos(self):
        p = self.paquete
        destino   = p.get("destino", "Destino")
        duracion  = p.get("duracion", 0)
        perfil    = p.get("perfil", "General")
        accesible = "Sí" if p.get("accesibilidad") else "No"

        self.setWindowTitle(f"Detalle · {destino}")
        self.lbl_nombre_paquete.setText(f"{destino} · {duracion} noches")
        self.lbl_meta.setText(f"Perfil: {perfil} · Accesible: {accesible}")
        self.chip_servicios.setText(p.get("servicios", "Servicios incluidos"))
        self.chip_accesibilidad.setText("Accesible" if p.get("accesibilidad") else "No accesible")
        self.chip_perfil.setText(perfil)
        self.lbl_descripcion.setText(p.get("descripcion", "Sin descripción"))

        self.stat_duracion_val.setText(str(duracion))

        self.dt_inicio.setDate(self.fecha)
        self.dt_fin.setDate(self.fecha.addDays(int(duracion)))

        self._actualizar_total()

    def _conectar_señales(self):
        self.dt_inicio.dateChanged.connect(self._actualizar_fecha_fin)
        self.dt_fin.dateChanged.connect(self._actualizar_total)
        self.spin_personas.valueChanged.connect(self._actualizar_total)
        self.btn_confirmar.clicked.connect(self._confirmar)
        self.btn_volver.clicked.connect(self._controlador.volver_a_principal)

    def _actualizar_fecha_fin(self):
        duracion = int(self.paquete.get("duracion", 0))
        nueva_fin = self.dt_inicio.date().addDays(duracion)
        self.dt_fin.blockSignals(True)
        self.dt_fin.setDate(nueva_fin)
        self.dt_fin.blockSignals(False)
        self._actualizar_total()

    def _actualizar_total(self):
        self.spin_personas.setValue(self.personas)
        personas = self.personas
        total    = self._controlador.calcular_total(self.paquete, personas) 

        try:
            precio = float(self.paquete.get("precio", 0))
        except (ValueError, TypeError):
            precio = 0.0

        self.lbl_total_valor.setText(f"{total:,.2f} €")
        self.lbl_total_sub.setText(f"{precio:,.2f} € × {personas} persona(s)")
        self.stat_total_val.setText(f"{total:,.2f} €")
        self.stat_precio_val.setText(f"{precio:,.2f} €")

    def _confirmar(self):
        fecha_ini = self.dt_inicio.date().toPyDate()
        fecha_fin = self.dt_fin.date().toPyDate()
        personas  = self.spin_personas.value()
        metodo    = self.combo_pago.currentText()

        # El controlador valida, la vista solo muestra el error
        ok, msg = self._controlador.validar_compra(
            self.paquete, fecha_ini, fecha_fin, personas, metodo
        )
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        total = self._controlador.calcular_total(self.paquete, personas)
        resp = QMessageBox.question(
            self, "Confirmar reserva",
            f"<b>{self.paquete.get('destino')}</b><br><br>"
            f"Fechas: {fecha_ini.strftime('%d/%m/%Y')} → {fecha_fin.strftime('%d/%m/%Y')}<br>"
            f"Personas: {personas}<br>"
            f"Método de pago: {metodo}<br><br>"
            f"<b>Total: {total:,.2f} €</b><br><br>"
            f"¿Confirmas la reserva?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        exito, mensaje = self._controlador.comprar_paquete(
            self.paquete, fecha_ini, fecha_fin, personas, metodo
        )
        if exito:
            QMessageBox.information(self, "Reserva confirmada", mensaje)
            self.close()
        else:
            QMessageBox.warning(self, "Error en la reserva", mensaje)
