class PedidoVO:
    def __init__(self, cliente_id, paquete_id, monto_total,
                 metodo_pago="PayPal", estado="Pendiente confirmacion",
                 fecha_inicio=None, fecha_fin=None, pedido_id=None,
                 nombre="", destino="", duracion="", servicios="", descripcion=""):
        self.cliente_id   = cliente_id
        self.paquete_id   = paquete_id
        self.monto_total  = monto_total
        self.metodo_pago  = metodo_pago
        self.estado       = estado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin    = fecha_fin
        self.pedido_id    = pedido_id    # None hasta que la BD lo asigna
        # Campos enriquecidos por JOIN con Paquetes_Turisticos
        self.nombre       = nombre
        self.destino      = destino
        self.duracion     = duracion
        self.servicios    = servicios
        self.descripcion  = descripcion

    @staticmethod
    def from_row(row):
        # Orden columnas (_SELECT de PedidoDAO con JOIN):
        # 0 pedido_id, 1 paquete_id, 2 nombre_paquete, 3 destino,
        # 4 duracion_dias, 5 servicios_incluidos, 6 descripcion_detallada,
        # 7 fecha_inicio, 8 fecha_fin, 9 monto_total,
        # 10 estado_pedido, 11 metodo_pago
        return PedidoVO(
            pedido_id   = row[0],
            paquete_id  = row[1],
            nombre      = row[2]  or "",
            destino     = row[3]  or "",
            duracion    = str(row[4]) if row[4] is not None else "",
            servicios   = row[5]  or "",
            descripcion = row[6]  or "",
            fecha_inicio= str(row[7]) if row[7] else None,
            fecha_fin   = str(row[8]) if row[8] else None,
            monto_total = float(row[9] or 0),
            estado      = row[10] or "Pendiente confirmacion",
            metodo_pago = row[11] or "PayPal",
            cliente_id  = 0,  # se sobreescribe en obtener_por_cliente
        )

    def to_insert_params(self):
        return [
            self.cliente_id,
            self.paquete_id,
            self.monto_total,
            self.metodo_pago,
            str(self.fecha_inicio) if self.fecha_inicio else None,
            str(self.fecha_fin)    if self.fecha_fin    else None,
        ]
