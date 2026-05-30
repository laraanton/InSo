class ReclamacionVO:
    """
    Value Object de Reclamación.
    Coincide con las columnas devueltas por ReclamacionDAO.
    """

    def __init__(
        self,
        reclamacion_id,
        pedido_id=None,
        cliente_id=None,
        pedido_ref="",
        cliente="",
        paquete="",
        destino="",
        fecha_pedido="",
        tipo="",
        descripcion="",
        estado="Registrada"
    ):

        self.reclamacion_id = reclamacion_id
        self.pedido_id = pedido_id
        self.cliente_id = cliente_id
        self.pedido_ref = pedido_ref
        self.cliente = cliente
        self.paquete = paquete
        self.destino = destino
        self.fecha_pedido = fecha_pedido
        self.tipo = tipo
        self.descripcion = descripcion
        self.estado = estado
