class GestionCompraVO:
    def __init__(self, pedido_id, paquete_id, cliente_id,
                 pedido_ref="", cliente="", email_cliente="",
                 paquete="", destino="", duracion=0,
                 fecha_inicio=None, fecha_fin=None,
                 monto_total=0.0, metodo_pago="PayPal",
                 estado="Pendiente confirmacion",
                 fecha_pedido="", num_personas=1):
        self.pedido_id     = pedido_id
        self.paquete_id    = paquete_id
        self.cliente_id    = cliente_id
        self.pedido_ref    = pedido_ref
        self.cliente       = cliente
        self.email_cliente = email_cliente
        self.paquete       = paquete
        self.destino       = destino
        self.duracion      = duracion
        self.fecha_pedido  = fecha_pedido
        self.fecha_inicio  = fecha_inicio
        self.fecha_fin     = fecha_fin
        self.monto_total   = monto_total
        self.metodo_pago   = metodo_pago
        self.estado        = estado
        self.num_personas  = num_personas