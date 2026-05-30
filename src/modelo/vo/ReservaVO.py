class ReservaVO:
    def __init__(self, id, cliente, paquete, fecha, precio, estado, metodo_pago,
                 pedido_id=0, cliente_id=0, paquete_id=0,
                 fecha_inicio=None, fecha_fin=None):
        self.id          = id           # identificador_unico 'ORD-N'
        self.identificador_unico = id
        self.cliente     = cliente
        self.paquete     = paquete
        self.fecha       = fecha        # 'YYYY-MM-DD'
        self.precio      = precio       # float sin formatear
        self.estado      = estado
        self.metodo_pago = metodo_pago
        # Internos — usados solo en DAO/controlador, no en la tabla
        self.pedido_id   = pedido_id
        self.cliente_id  = cliente_id
        self.paquete_id  = paquete_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin    = fecha_fin

    @staticmethod
    def from_row(row):
        # Orden columnas (_SELECT de ReservaDAO):
        # 0 pedido_id, 1 identificador_unico, 2 nombre_completo,
        # 3 nombre_paquete, 4 fecha_pedido, 5 monto_total,
        # 6 estado_pedido, 7 metodo_pago, 8 cliente_id, 9 paquete_id
        return ReservaVO(
            id          = row[1] or f"ORD-{row[0]}",
            cliente     = row[2] or "",
            paquete     = row[3] or "",
            fecha       = row[4] or "",
            precio      = float(row[5] or 0),
            estado      = row[6] or "Pendiente confirmacion",
            metodo_pago = row[7] or "PayPal",
            pedido_id   = row[0],
            cliente_id  = row[8],
            paquete_id  = row[9],
        )

    def precio_fmt(self):
        """Precio formateado para pantalla: 1200.0 → '1.200,00 EUR'"""
        return (
            f"{self.precio:,.2f} EUR"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def to_export_dict(self):
        """Solo para escritura CSV — único sitio donde se permite un dict."""
        return {
            "id":          self.id,
            "cliente":     self.cliente,
            "paquete":     self.paquete,
            "fecha":       self.fecha,
            "precio":      self.precio_fmt(),
            "estado":      self.estado,
            "metodo_pago": self.metodo_pago,
        }
