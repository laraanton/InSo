from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

Form, Window = uic.loadUiType("./src/vista/ui/vistaDetallePedido.ui")


class VentanaDetalleMViaje(QMainWindow, Form):
    def __init__(self, user, pedido: dict):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.pedido = pedido
        self._controlador = None

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self.pedido = self._controlador.formatear_pedido(self.pedido)
        self._rellenar_datos()
        self._conectar_señales()

    def _rellenar_datos(self):
        p = self.pedido
        self.setWindowTitle(f"Viaje · {p.get('destino', 'Destino')}")
        self.lbl_nombre_paquete.setText(
            f"{p.get('destino', 'Destino')} · {p.get('duracion', 0)} noches"
        )
        self.lbl_meta.setText(
            f"Pedido #{p.get('pedido_id', '—')} · {p.get('estado', '—')}"
        )
        self.chip_servicios.setText(p.get("servicios", "") or "—")
        self.chip_metodo_pago.setText(p.get("metodo_pago", "—"))
        self.chip_estado.setText(p.get("estado", "—"))
        self.stat_duracion_val.setText(str(p.get("duracion", 0)))
        self.stat_precio_val.setText(f"{p['monto_total']:,.2f} €")
        self.stat_total_val.setText(f"{p.get('duracion', 0)} noches")
        self.lbl_descripcion.setText(p.get("descripcion", "Sin descripción"))
        self.lbl_val_inicio.setText(p["fecha_inicio_fmt"])
        self.lbl_val_fin.setText(p["fecha_fin_fmt"])
        self.lbl_val_pago.setText(p.get("metodo_pago", "—"))
        self.lbl_val_total.setText(f"{p['monto_total']:,.2f} €")
        self.lbl_val_estado.setText(p.get("estado", "—"))
        self.lbl_val_pedido.setText(f"#{p.get('pedido_id', '—')}")

    def _configurar_resena(self):
        """Bloquea el formulario si ya existe reseña para este pedido."""
        pedido_id = self.pedido.get("pedido_id")
        if pedido_id and self._controlador.tiene_feedback(pedido_id):
            self._bloquear_formulario_resena()

    def _bloquear_formulario_resena(self):
        """Deshabilita todos los controles y muestra el mensaje de confirmación."""
        self.spin_val_general.setEnabled(False)
        self.spin_val_trato.setEnabled(False)
        self.spin_val_transporte.setEnabled(False)
        self.spin_val_alojamiento.setEnabled(False)
        self.txt_comentario.setEnabled(False)
        self.btn_enviar_resena.setEnabled(False)
        self.lbl_resena_enviada.setVisible(True)
        self.resena_subtitulo.setText("Ya has valorado este viaje.")

    def _conectar_señales(self):
        self.btn_volver.clicked.connect(self._controlador.ir_a_mis_viajes)
        self.btn_enviar_resena.clicked.connect(self._enviar_resena)   # ✅

    def _enviar_resena(self):
        pedido_id = self.pedido.get("pedido_id")
        if not pedido_id:
            return

        ok, msg = self._controlador.guardar_feedback(
            pedido_id,
            self.spin_val_general.value(),
            self.spin_val_trato.value(),
            self.spin_val_transporte.value(),
            self.spin_val_alojamiento.value(),
            self.txt_comentario.toPlainText(),
        )

        if ok:
            QMessageBox.information(self, "Reseña enviada", msg)
            self._bloquear_formulario_resena()   # bloquea tras enviar
        else:
            QMessageBox.warning(self, "Error", msg)
