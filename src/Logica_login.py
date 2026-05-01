from src.modelo.dao.UserDAO import UserDAO
from src.modelo.vo.LoginVO import LoginVO

class BussinessObject():

    def comprobarLogin(self, email, password_hash):
        if not email or not password_hash:
            return None, "Email y contraseña obligatorios"

        loginVO = LoginVO(email, password_hash)
        user = UserDAO().consultaLogin(loginVO)

        if not user:
            return None, "Credenciales incorrectas"

        if not user.es_activo():
            if user.cuenta_bloqueada:
                return None, "Cuenta bloqueada. Contacta con el administrador"
            return None, "Cuenta suspendida"

        return user, "Inicio de sesión exitoso"

    def verificarCorreo(self, email):
        if not email:
            return None, "Debe ingresar el email"

        usuario = UserDAO().obtenerUsuarioPorEmail(email)
        if usuario:
            return usuario.email, "Correo verificado"
        return None, "El correo no está registrado"

    def actualizarContrasena(self, email, nueva_contrasena):
        if not nueva_contrasena or len(nueva_contrasena) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"

        usuario = UserDAO().obtenerUsuarioPorEmail(email)
        if not usuario:
            return False, "No existe ninguna cuenta con ese email"

        exito = UserDAO().actualizarContrasena(usuario.usuario_id, nueva_contrasena)
        if exito:
            return True, "Contraseña actualizada correctamente"
        return False, "No se pudo actualizar la contraseña"
