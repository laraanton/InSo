class RegistroVO:
    def __init__(self, dni_nie, nombre_completo, email, telefono, password_hash,
                 tipo_usuario="Cliente", preferencia="General",
                 preferencia_accesibilidad="Ninguna"):
        self.dni_nie = dni_nie
        self.nombre_completo = nombre_completo
        self.email = email
        self.telefono = telefono
        self.password_hash = password_hash
        self.tipo_usuario = tipo_usuario
        self.preferencia = preferencia
        self.preferencia_accesibilidad = preferencia_accesibilidad
