from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaDetallePedido.ui")


class VentanaDetalleMViaje(QMainWindow, Form):
    def __init__(self, user, pedido: dict):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.pedido = pedido
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_detalle = self
        self._rellenar_datos()
        self._conectar_señales()

    def _rellenar_datos(self):
        p = self.pedido

        destino  = p.get("destino", "Destino")
        duracion = p.get("duracion", 0)
        servicios   = p.get("servicios", "") or "—"
        descripcion = p.get("descripcion", "Sin descripción")
        monto_total = float(p.get("monto_total", 0))
        metodo_pago = p.get("metodo_pago", "—")
        estado      = p.get("estado", "—")
        pedido_id   = p.get("pedido_id", "—")

        fecha_ini = str(p.get("fecha_inicio", ""))[:10]
        fecha_fin = str(p.get("fecha_fin", ""))[:10]

        # Formatear fechas DD/MM/YYYY si vienen como YYYY-MM-DD
        def fmt(f):
            try:
                y, m, d = f.split("-")
                return f"{d}/{m}/{y}"
            except Exception:
                return f or "—"

        self.setWindowTitle(f"Viaje · {destino}")
        self.lbl_nombre_paquete.setText(f"{destino} · {duracion} noches")
        self.lbl_meta.setText(f"Pedido #{pedido_id} · {estado}")

        self.chip_servicios.setText(servicios)
        self.chip_metodo_pago.setText(metodo_pago)
        self.chip_estado.setText(estado)

        self.stat_duracion_val.setText(str(duracion))
        self.stat_precio_val.setText(f"{monto_total:,.2f} €")
        self.stat_total_val.setText(f"{duracion} noches")

        self.lbl_descripcion.setText(descripcion)

        self.lbl_val_inicio.setText(fmt(fecha_ini))
        self.lbl_val_fin.setText(fmt(fecha_fin))
        self.lbl_val_pago.setText(metodo_pago)
        self.lbl_val_total.setText(f"{monto_total:,.2f} €")
        self.lbl_val_estado.setText(estado)
        self.lbl_val_pedido.setText(f"#{pedido_id}")

    def _conectar_señales(self):
        self.btn_volver.clicked.connect(self.controlador.ir_a_mis_viajes)
