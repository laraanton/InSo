class OperacionResultadoVO:
    """
    VO genérico para operaciones de escritura (crear, editar, eliminar,
    cambiar estado…). Transporta el resultado sin exponer detalles internos.
    """
    def _init_(self, ok: bool, mensaje: str):
        self.ok      = ok
        self.mensaje = mensaje