from datetime import date

from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaDetallePaquete.ui")


class VentanaDetallePaquete(QMainWindow, Form):
    def __init__(self, user, paquete: dict):
        super().__init__()

        self.setupUi(self)

        self.user = user
        self.paquete = paquete
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_detalle = self

        self._rellenar_datos()
        self._conectar_señales()

    def _rellenar_datos(self):
        p = self.paquete

        destino = p.get("destino", "Destino")
        duracion = p.get("duracion", 0)
        perfil = p.get("perfil", "General")
        accesible = "Sí" if p.get("accesibilidad") else "No"
        descripcion = p.get("descripcion", "Sin descripción")
        servicios = p.get("servicios", "Servicios incluidos")
        precio = float(p.get("precio", 0))

        self.setWindowTitle(f"Detalle · {destino}")

        self.lbl_nombre_paquete.setText(
            f"{destino} · {duracion} noches"
        )

        self.lbl_meta.setText(
            f"Perfil: {perfil} · Accesible: {accesible}"
        )

        self.chip_servicios.setText(servicios)
        self.chip_accesibilidad.setText(
            "Accesible" if p.get("accesibilidad") else "No accesible"
        )
        self.chip_perfil.setText(perfil)

        self.stat_duracion_val.setText(str(duracion))
        self.stat_precio_val.setText(f"{precio:,.2f} €")
        self.stat_total_val.setText(f"{precio:,.2f} €")

        # ── Descripción
        self.lbl_descripcion.setText(descripcion)

        # ── Fechas por defecto
        hoy = QDate.currentDate()

        self.dt_inicio.setDate(hoy)
        self.dt_fin.setDate(hoy.addDays(int(duracion)))

        self._actualizar_total()

    def _conectar_señales(self):
        self.dt_inicio.dateChanged.connect(self._actualizar_fecha_fin)
        self.dt_fin.dateChanged.connect(self._actualizar_total)
        self.spin_personas.valueChanged.connect(self._actualizar_total)
        self.btn_confirmar.clicked.connect(self._confirmar)
        self.btn_volver.clicked.connect(self.controlador.volver_a_principal)

    def _actualizar_fecha_fin(self):
        duracion = int(self.paquete.get("duracion", 0))
        nueva_fin = self.dt_inicio.date().addDays(duracion)
        # Bloquear señal para no disparar _actualizar_total dos veces
        self.dt_fin.blockSignals(True)
        self.dt_fin.setDate(nueva_fin)
        self.dt_fin.blockSignals(False)
        self._actualizar_total()
  
    def _actualizar_total(self):

        try:
            precio = float(self.paquete.get("precio", 0))
        except (ValueError, TypeError):
            precio = 0.0

        personas = self.spin_personas.value()

        total = precio * personas

        self.lbl_total_valor.setText(
            f"{total:,.2f} €"
        )

        self.lbl_total_sub.setText(
            f"{precio:,.2f} € × {personas} persona(s)"
        )

        self.stat_total_val.setText(
            f"{total:,.2f} €"
        )

    def _confirmar(self):

        fecha_ini = self.dt_inicio.date().toPyDate()
        fecha_fin = self.dt_fin.date().toPyDate()
        dias_exactos = (fecha_fin - fecha_ini).days


        personas = self.spin_personas.value()
        metodo = self.combo_pago.currentText()

        # ── Validaciones

        if fecha_ini < date.today():
            QMessageBox.warning(
                self,
                "Fecha inválida",
                "La fecha de inicio no puede ser anterior a hoy.",
            )

            self.dt_inicio.setFocus()
            return
        
        if dias_exactos != int(self.paquete.get("duracion", 0)):
            QMessageBox.warning(
                self,
                "Duracion",
                "La duración del paquete no es flexible",
            )
            return

        if fecha_fin <= fecha_ini:
            QMessageBox.warning(
                self,
                "Fechas incorrectas",
                "La fecha de fin debe ser posterior a la de inicio.",
            )

            self.dt_fin.setFocus()
            return

        if personas < 1:
            QMessageBox.warning(
                self,
                "Personas",
                "Debe haber al menos 1 persona.",
            )
            return

        try:
            precio = float(self.paquete.get("precio", 0))
        except (ValueError, TypeError):
            precio = 0.0
        total = precio * personas

        resp = QMessageBox.question(
            self,
            "Confirmar reserva",
            (
                f"<b>{self.paquete.get('destino')}</b><br><br>"
                f"Fechas: "
                f"{fecha_ini.strftime('%d/%m/%Y')} → "
                f"{fecha_fin.strftime('%d/%m/%Y')}<br>"
                f"Personas: {personas}<br>"
                f"Método de pago: {metodo}<br><br>"
                f"<b>Total: {total:,.2f} €</b><br><br>"
                f"¿Confirmas la reserva?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resp != QMessageBox.Yes:
            return

        exito, mensaje = self.controlador.comprar_paquete(
            self.paquete,
            fecha_ini,
            fecha_fin,
            personas,
            metodo
        )

        if exito:
            QMessageBox.information(
                self,
                "Reserva confirmada",
                mensaje
            )
            self.close()

        else:
            QMessageBox.warning(
                self,
                "Error en la reserva",
                mensaje
            )
