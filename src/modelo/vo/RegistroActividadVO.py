"""
RegistroActividadVO.py  –  Value Object del Registro de Actividad
=================================================================
Contenedor de solo datos para una fila de Registro_Actividad.
Sin lógica de negocio ni acceso a BD.
"""


class RegistroActividadVO:
    """Representa una entrada del log de actividad del sistema."""

    def __init__(self, actividad_id, fecha, nombre_usuario,
                 tipo_usuario, tipo_accion, detalle, ip):
        self._actividad_id   = actividad_id
        self._fecha          = fecha
        self._nombre_usuario = nombre_usuario
        self._tipo_usuario   = tipo_usuario
        self._tipo_accion    = tipo_accion
        self._detalle        = detalle
        self._ip             = ip

    @property
    def actividad_id(self):
        return self._actividad_id

    @property
    def fecha(self):
        return self._fecha

    @property
    def nombre_usuario(self):
        return self._nombre_usuario

    @property
    def tipo_usuario(self):
        return self._tipo_usuario

    @property
    def tipo_accion(self):
        return self._tipo_accion

    @property
    def detalle(self):
        return self._detalle

    @property
    def ip(self):
        return self._ip

    def __repr__(self):
        return (f"RegistroActividadVO({self._actividad_id}, "
                f"{self._fecha}, {self._nombre_usuario}, {self._tipo_accion})")
