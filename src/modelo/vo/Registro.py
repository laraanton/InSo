
class RegistroVO:
    def __init__(self, dni_nie, nombre_completo, email, 
                 telefono, password_hash, tipo_usuario='Cliente'):
        self.__dni_nie         = dni_nie
        self.__nombre_completo = nombre_completo
        self.__email           = email
        self.__telefono        = telefono
        self.__password_hash   = password_hash
        self.__tipo_usuario    = tipo_usuario  # por defecto Cliente

    @property
    def dni_nie(self):
        return self.__dni_nie

    @property
    def nombre_completo(self):
        return self.__nombre_completo

    @property
    def email(self):
        return self.__email

    @property
    def telefono(self):
        return self.__telefono

    @property
    def password_hash(self):
        return self.__password_hash

    @property
    def tipo_usuario(self):
        return self.__tipo_usuario
