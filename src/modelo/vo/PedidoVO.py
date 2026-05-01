
class PedidoVO:
    def __init__(self, cliente_id, paquete_id, monto_total,
                 metodo_pago='PayPal', fecha_inicio=None, fecha_fin=None):
        self.__cliente_id   = cliente_id
        self.__paquete_id   = paquete_id
        self.__monto_total  = monto_total
        self.__metodo_pago  = metodo_pago
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin    = fecha_fin

    @property
    def cliente_id(self):
        return self.__cliente_id

    @property
    def paquete_id(self):
        return self.__paquete_id

    @property
    def monto_total(self):
        return self.__monto_total

    @property
    def metodo_pago(self):
        return self.__metodo_pago

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @property
    def fecha_fin(self):
        return self.__fecha_fin
