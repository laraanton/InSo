
class UsuarioVO:
    def __init__(self, usuario_id, dni_nie, nombre_completo, email,
                 telefono, tipo_usuario, estado, cuenta_bloqueada,
                 fecha_registro=None, password_hash=None):
        self._usuario_id      = usuario_id
        self._dni_nie         = dni_nie
        self._nombre_completo = nombre_completo
        self._email           = email
        self._telefono        = telefono
        self._tipo_usuario    = tipo_usuario   # : Administrador, Operador, CLiente
        self._estado          = estado   # :Activo, Inactivo, Suspendido
        self._cuenta_bloqueada = cuenta_bloqueada  # True / False
        self._fecha_registro  = fecha_registro

    @property
    def usuario_id(self):
        return self._usuario_id

    @property
    def dni_nie(self):
        return self._dni_nie

    @property
    def nombre_completo(self):
        return self._nombre_completo

    @property
    def email(self):
        return self._email

    @property
    def telefono(self):
        return self._telefono

    @property
    def tipo_usuario(self):
        return self._tipo_usuario

    @property
    def estado(self):
        return self._estado

    @property
    def cuenta_bloqueada(self):
        return self._cuenta_bloqueada

    @property
    def fecha_registro(self):
        return self._fecha_registro

    def es_activo(self):
        return self._estado == 'Activo' and not self._cuenta_bloqueada

    def __repr__(self):
        return f"UsuarioVO({self._usuario_id}, {self._nombre_completo}, {self._tipo_usuario})"
