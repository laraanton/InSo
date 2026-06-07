from src.modelo.dao.UserDAO import UserDAO
from src.modelo.vo.LoginVO import LoginVO
from src.modelo.vo.RegistroVO import RegistroVO

class BussinessObject():
    _intentos = {}
    def comprobarLogin(self, email, password):
        if not email or not password:
            return None, "Email y contraseña obligatorios"

        if email in self._intentos and self._intentos[email] >= 5:
            return None, "Has superado tu límite de intentos. ¡Vuelve más tarde!"
    
        loginVO = LoginVO(email, password)
        user = UserDAO().consultaLogin(loginVO)

        if not user:
            if email in self._intentos:
                self._intentos[email] += 1
            else:
                self._intentos[email] = 1
                
            if self._intentos[email] >= 5:
                return None, "Has superado tu límite de intentos. ¡Vuelve más tarde!"
            return None, "Credenciales incorrectas"

        self._intentos[email] = 0
        
        #Sin control de intentos
        #if not user:
        #    return None, "Credenciales incorrectas"

        if not user.es_activo():
            if user.cuenta_bloqueada:
                return None, "Cuenta bloqueada. Contacta con el administrador"
            return None, "Cuenta inactiva o suspendida"

        return user, "Inicio de sesión exitoso"

    def verificarCorreo(self, email):
        if not email:
            return None, "Debe ingresar el email"

        usuario = UserDAO().obtenerUsuarioPorEmail(email)
        if usuario:
            return usuario.email, "Correo verificado"
        return None, "El correo no está registrado"

    def actualizarContrasena(self, email, nueva_contrasena, dni):
        if not nueva_contrasena or len(nueva_contrasena) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
            
        if not dni:
            return False, "El DNI es obligatorio"
            
        usuario = UserDAO().obtenerUsuarioPorEmail(email)
        if not usuario:
            return False, "No existe ninguna cuenta con ese email"
        if usuario.dni_nie.upper() != dni.upper():
            return False, "El DNI no corresponde con el email introducido"
        
        exito = UserDAO().actualizarContrasena(usuario.usuario_id, nueva_contrasena)
        if exito:
            return True, "Contraseña actualizada correctamente"
        return False, "No se pudo actualizar la contraseña"
    

    def registrarUsuario(self, dni_nie, nombre_completo, email, telefono, password, preferencia, accesibilidad):
        if not all([dni_nie, nombre_completo, email, password]):
            return False, "Todos los campos obligatorios deben estar rellenos"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"

        registroVO = RegistroVO(dni_nie, nombre_completo, email, telefono, password, preferencia = preferencia, preferencia_accesibilidad=accesibilidad)
        exito = UserDAO().insertarUsuario(registroVO)

        if exito:
            return True, "Usuario registrado correctamente"
        return False, "No se pudo registrar el usuario. El email o DNI ya existen"

