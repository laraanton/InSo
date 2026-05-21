from src.modelo.Logica_login import BussinessObject
from src.vista.VentanaCliente import VentanaCliente
from src.vista.VentanaAjustesCuenta import VentanaAjustesCuenta
from src.vista.VentanaMisViajes import VentanaMisViajes
from src.vista.Login import MiVentana
from src.modelo.dao.UserDAO import UserDAO
from src.modelo.vo.LoginVO import LoginVO
from src.modelo.dao.UserDAO import UserDAO

class ControladorCliente:
    def __init__(self, user):
        self.user = user
        self.logica = BussinessObject()
        self.ventana_principal = None
        self.ventana_ajustes = None
        self.ventana_viajes = None

    def abrir_principal(self):
        self.ventana_principal = VentanaCliente(self.user, self)
        self.ventana_principal.show()
    
    def ir_a_ajustes(self):
        self.ventana_ajustes = VentanaAjustesCuenta(self.user, self)
        self.ventana_ajustes.show()
        if self.ventana_principal:
            self.ventana_principal.hide()
    
    def ir_a_mis_viajes(self):
        self.ventana_viajes = VentanaMisViajes(self.user, self)
        self.ventana_ajustes.show()
        if self.ventana_ajustes:
            self.ventana_ajustes.hide()
        if self.ventana_principal:
            self.ventana_principal.hide()

    def cerrar_sesion(self):
        self.ventana_login = MiVentana()
        self.ventana_login.show()
        self._cerrar_todo()
    
    def _cerrar_todo(self):
        for v in [self.ventana_principal, self.ventana_ajustes, self.ventana_viajes]:
            if v:
                v.close()
    
    def volver_a_principal(self):
        self.abrir_principal()
        if self.ventana_ajustes:
            self.ventana_ajustes.hide()
        if self.ventana_viajes:
            self.ventana_viajes.hide()
    
    def guardar_perfil(self, telefono, preferencia):
        from src.modelo.dao.UserDAO import UserDAO
        dao = UserDAO()
        exito_tel = True
        exito_pref = True

        if telefono != self.user.telefono:
            exito_tel = dao.actualizarTelefono(self.user.usuario_id, telefono)

        if preferencia != self.user.preferencia:
            exito_pref = dao.actualizarPreferencia(self.user.usuario_id, preferencia)

        if exito_tel and exito_pref:
            # Actualiza el user en memoria
            self.user = dao.obtenerUsuarioPorId(self.user.usuario_id)
            return True, "Perfil actualizado correctamente"
        return False, "No se pudo actualizar el perfil"

    def cambiar_contrasena(self, pass_actual, pass_nueva, pass_confirmar):
        if not pass_actual or not pass_nueva or not pass_confirmar:
            return False, "Todos los campos son obligatorios"

        if pass_nueva != pass_confirmar:
            return False, "Las contraseñas nuevas no coinciden"

        if len(pass_nueva) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"

        # Verifica que la contraseña actual sea correcta
        from src.modelo.vo.LoginVO import LoginVO
        from src.modelo.dao.UserDAO import UserDAO
        loginVO = LoginVO(self.user.email, pass_actual)
        user_check = UserDAO().consultaLogin(loginVO)
        if not user_check:
            return False, "La contraseña actual no es correcta"

        exito, mensaje = self.logica.actualizarContrasena(self.user.email, pass_nueva)
        return exito, mensaje
        
