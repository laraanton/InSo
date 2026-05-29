class UsuarioVO:
    def __init__(self, usuario_id, dni_nie, nombre_completo, email, telefono,
                 tipo_usuario, estado, preferencia, cuenta_bloqueada,
                 fecha_registro=None, preferencia_accesibilidad="Ninguna",
                 password_hash=None):
        self.usuario_id = usuario_id
        self.dni_nie = dni_nie
        self.nombre_completo = nombre_completo
        self.email = email
        self.telefono = telefono
        self.tipo_usuario = tipo_usuario
        self.estado = estado
        self.preferencia = preferencia
        self.cuenta_bloqueada = cuenta_bloqueada
        self.fecha_registro = fecha_registro
        self.preferencia_accesibilidad = preferencia_accesibilidad
        self.password_hash = password_hash

    def es_activo(self):
        return self.estado == "Activo" and not self.cuenta_bloqueada

    @staticmethod
    def from_row(row):
        return UsuarioVO(
            usuario_id = row[0],
            dni_nie = row[1] or "",
            nombre_completo = row[2] or "",
            email = row[3] or "",
            telefono = row[4] or "",
            tipo_usuario = row[5] or "Cliente",
            estado = row[6] or "Activo",
            preferencia = row[7] or "General",
            cuenta_bloqueada = bool(row[8]),
            fecha_registro = row[9]  if len(row) > 9  else None,
            preferencia_accesibilidad = row[10] if len(row) > 10 else "Ninguna",
            password_hash = row[11] if len(row) > 11 else None,
        )

    def __repr__(self):
        return f"UsuarioVO({self.usuario_id}, {self.nombre_completo}, {self.tipo_usuario})"
