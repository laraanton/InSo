from src.modelo.Logica_login import BussinessObject

class ControladorPrincipal:
    def __init__(self):
        self._modelo = BussinessObject()
        self._ventana_actual = None

    # ── Navegación ────────────────────────────────────────────────────────────

    def abrirIniciarSesion(self):
        from src.vista.Login import MiVentana
        self._cambiar_ventana(MiVentana(self))

    def abrirRegistro(self):
        from src.vista.VentanaRegistro import VentanaRegistro
        self._cambiar_ventana(VentanaRegistro(self))

    def abrirRecuperar(self):
        from src.vista.VentanaRecuperar import VentanaRecuperar
        self._cambiar_ventana(VentanaRecuperar(self))

    def abrirVentanaPrincipal(self, user):
        tipo = user.tipo_usuario
        if tipo == "Administrador":
            from src.vista.VentanaAdmin import VentanaAdmin
            self._cambiar_ventana(VentanaAdmin(user))
        elif tipo == "Operador":
            from src.vista.VentanaOperador import VentanaOperador
            self._cambiar_ventana(VentanaOperador(user))
        elif tipo == "Cliente":
            from src.vista.VentanaCliente import VentanaCliente
            self._cambiar_ventana(VentanaCliente(user))

    def _cambiar_ventana(self, nueva_ventana):
        if self._ventana_actual:
            self._ventana_actual.close()
        self._ventana_actual = nueva_ventana
        self._ventana_actual.show()

    # ── Lógica: delega al modelo ──────────────────────────────────────────────

    def comprobarLogin(self, email, password):
        return self._modelo.comprobarLogin(email, password)

    def registrarUsuario(self, *args, **kwargs):
        return self._modelo.registrarUsuario(*args, **kwargs)

    def actualizarContrasena(self, *args, **kwargs):
        return self._modelo.actualizarContrasena(*args, **kwargs)
