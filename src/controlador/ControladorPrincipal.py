from src.vista.VentanaAdmin import VentanaAdmin
from src.vista.VentanaOperador import VentanaOperador
from src.vista.VentanaCliente import VentanaCliente
from src.controlador.ControladorAdmin import ControladorAdmin
from src.controlador.ControladorOperador import ControladorOperador
from src.controlador.ControladorCliente import ControladorCliente

class ControladorPrincipal:
    def __init__(self, ventanaLogin, modelo):
        self._ventanaLogin = ventanaLogin
        self._modelo = modelo
        self._ventana_actual = None

    def ventanaInciarSesion(self):
        self._ventanaLogin.show()

    def abrirRegistro(self):
        from src.vista.VentanaRegistro import VentanaRegistro
        self._cambiar_ventana(VentanaRegistro(self))

    def abrirRecuperar(self):
        from src.vista.VentanaRecuperar import VentanaRecuperar
        self._cambiar_ventana(VentanaRecuperar(self))

    def abrirVentanaPrincipal(self, user):
        self._ventanaLogin.hide()
        tipo = user.tipo_usuario
        if tipo == "Administrador":
            self._ventana_actual = VentanaAdmin(user)
            self._ventana_actual.controlador = ControladorAdmin(user, self)
        elif tipo == "Operador":
            self._ventana_actual = VentanaOperador(user)
            ctrl = ControladorOperador(usuario_id=user.usuario_id, ventana=self._ventana_actual, controlador_principal=self
            )
            self._ventana_actual.controlador = ctrl
        elif tipo == "Cliente":
            self._ventana_actual = VentanaCliente(user)
            self._ventana_actual.controlador = ControladorCliente(user, self)

        if self._ventana_actual:
            self._ventana_actual.show()

    def cerrarSesion(self):
        if self._ventana_actual:
            self._ventana_actual.close()
            self._ventana_actual = None
        self._ventanaLogin.resetear()
        self._ventanaLogin.show()

    def _cambiar_ventana(self, nueva_ventana):
        if self._ventana_actual:
            self._ventana_actual.close()
        self._ventana_actual = nueva_ventana
        self._ventana_actual.show()

    def comprobarLogin(self, email, password):
        return self._modelo.comprobarLogin(email, password)

    def registrarUsuario(self, *args, **kwargs):
        return self._modelo.registrarUsuario(*args, **kwargs)

    def actualizarContrasena(self, *args, **kwargs):
        return self._modelo.actualizarContrasena(*args, **kwargs) self._modelo.actualizarContrasena(*args, **kwargs)
