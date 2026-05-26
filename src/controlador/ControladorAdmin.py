import socket
from src.modelo.dao.AdminDAO import AdminDAO


class ControladorAdmin:

    def __init__(self, usuario_actual):
        self.usuario_actual = usuario_actual
        self._dao = AdminDAO()

    def _ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

    def _registrar(self, tipo_accion, detalle):
        self._dao.registrarActividad(
            self.usuario_actual.usuario_id, tipo_accion, detalle, self._ip()
        )

    def obtener_todos_los_usuarios(self):
     
        return self._dao.obtenerTodosLosUsuarios()

    def bloquear_cuenta(self, usuario):
     
        self._dao.bloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta bloqueada: {usuario.email}")

    def desbloquear_cuenta(self, usuario):

        self._dao.desbloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")

    def obtener_operadores(self):
        return self._dao.obtenerOperadores()

    def crear_operador(self, dni_nie, nombre_completo, email, telefono, password):
        exito, msg = self._dao.crearOperador(
            dni_nie, nombre_completo, email, telefono, password
        )
        if exito:
            self._registrar("Creación", f"Nuevo operador: {email}")
        return exito, msg

    def actualizar_operador(self, usuario, telefono, estado, password=None):
        self._dao.actualizarOperador(
            usuario.usuario_id, telefono, estado, password or None
        )
        self._registrar("Modificación", f"Operador editado: {usuario.email}")

    def bloquear_operador(self, usuario):

        self._dao.bloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta bloqueada: {usuario.email}")

    def desbloquear_operador(self, usuario):
        self._dao.desbloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")


    def obtener_actividad(self, tipo_accion=None, limite=200):
        return self._dao.obtenerActividad(tipo_accion=tipo_accion, limite=limite)


    def hacer_backup(self, ruta_carpeta):
     
        exito, resultado = self._dao.hacerBackup(ruta_carpeta)
        if exito:
            self._registrar("Backup", f"Backup generado: {resultado}")
        return exito, resultado
