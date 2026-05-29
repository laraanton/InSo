class FeedbackVO:
    def __init__(self, feedback_id, pedido_id, cliente_id,
                 pedido_ref="", cliente="", paquete="", destino="",
                 fecha_viaje="",
                 val_general=None, val_trato_operador=None,
                 val_calidad_transporte=None, val_satisfaccion_alojamiento=None,
                 comentarios=""):
        self.feedback_id                  = feedback_id
        self.pedido_id                    = pedido_id
        self.cliente_id                   = cliente_id
        self.pedido_ref                   = pedido_ref
        self.cliente                      = cliente
        self.paquete                      = paquete
        self.destino                      = destino
        self.fecha_viaje                  = fecha_viaje
        self.val_general                  = val_general
        self.val_trato_operador           = val_trato_operador
        self.val_calidad_transporte       = val_calidad_transporte
        self.val_satisfaccion_alojamiento = val_satisfaccion_alojamiento
        self.comentarios                  = comentarios