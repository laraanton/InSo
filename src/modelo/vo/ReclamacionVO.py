class ReclamacionVO:
    def __init__(self, reclamacion_id, pedido_id, cliente_id,
                 pedido_ref="", cliente="", paquete="", destino="",
                 fecha_pedido="", tipo="Otro", descripcion="",
                 estado="Pendiente", respuesta_operador="",
                 fecha_reclamacion="", fecha_resolucion=""):
        self.reclamacion_id     = reclamacion_id
        self.pedido_id          = pedido_id
        self.cliente_id         = cliente_id
        self.pedido_ref         = pedido_ref
        self.cliente            = cliente
        self.paquete            = paquete
        self.destino            = destino
        self.fecha_pedido       = fecha_pedido
        self.tipo               = tipo
        self.descripcion        = descripcion
        self.estado             = estado
        self.respuesta_operador = respuesta_operador
        self.fecha_reclamacion  = fecha_reclamacion
        self.fecha_resolucion   = fecha_resolucion