from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaDetallePedido.ui")


class VentanaDetalleMViaje(QMainWindow, Form):
    def __init__(self, user, pedido: dict):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_detalle = self
        # El controlador formatea los datos antes de dárselos a la vista
        self.pedido = self.controlador.formatear_pedido(pedido) 
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

        # Las fechas ya vienen formateadas del controlador
        self.lbl_val_inicio.setText(p["fecha_inicio_fmt"])
        self.lbl_val_fin.setText(p["fecha_fin_fmt"])
        self.lbl_val_pago.setText(p.get("metodo_pago", "—"))
        self.lbl_val_total.setText(f"{p['monto_total']:,.2f} €")
        self.lbl_val_estado.setText(p.get("estado", "—"))
        self.lbl_val_pedido.setText(f"#{p.get('pedido_id', '—')}")

    def _conectar_señales(self):
        self.btn_volver.clicked.connect(self.controlador.ir_a_mis_viajes)
