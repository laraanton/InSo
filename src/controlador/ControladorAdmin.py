"""
ControladorAdmin.py  —  Controlador (MVC)
==========================================
Intermediario entre las vistas de administración y AdminDAO.
Las vistas nunca llaman al DAO directamente; toda la lógica de
coordinación pasa por este controlador.

Responsabilidades:
    - Exponer métodos de alto nivel que las vistas necesitan.
    - Delegar la persistencia al AdminDAO.
    - Registrar actividad automáticamente cuando procede.
"""

import socket
from src.modelo.dao.AdminDAO import AdminDAO


class ControladorAdmin:

    def __init__(self, usuario_actual):
        self.usuario_actual = usuario_actual
        self._dao = AdminDAO()

    # ------------------------------------------------------------------ #
    #  Utilidades internas                                                 #
    # ------------------------------------------------------------------ #

    def _ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

    def _registrar(self, tipo_accion, detalle):
        self._dao.registrarActividad(
            self.usuario_actual.usuario_id, tipo_accion, detalle, self._ip()
        )

    # ------------------------------------------------------------------ #
    #  Usuarios                                                            #
    # ------------------------------------------------------------------ #

    def obtener_todos_los_usuarios(self):
        """Devuelve la lista completa de UsuarioVO."""
        return self._dao.obtenerTodosLosUsuarios()

    def bloquear_cuenta(self, usuario):
        """Bloquea la cuenta e inscribe la acción en el registro."""
        self._dao.bloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta bloqueada: {usuario.email}")

    def desbloquear_cuenta(self, usuario):
        """Desbloquea la cuenta e inscribe la acción en el registro."""
        self._dao.desbloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")

    # ------------------------------------------------------------------ #
    #  Operadores                                                          #
    # ------------------------------------------------------------------ #

    def obtener_operadores(self):
        """Devuelve la lista de UsuarioVO con tipo_usuario = 'Operador'."""
        return self._dao.obtenerOperadores()

    def crear_operador(self, dni_nie, nombre_completo, email, telefono, password):
        """
        Crea un nuevo operador.
        Devuelve (True, mensaje) o (False, mensaje_error).
        Si tiene éxito registra la actividad.
        """
        exito, msg = self._dao.crearOperador(
            dni_nie, nombre_completo, email, telefono, password
        )
        if exito:
            self._registrar("Creación", f"Nuevo operador: {email}")
        return exito, msg

    def actualizar_operador(self, usuario, telefono, estado, password=None):
        """
        Actualiza datos de un operador y registra la modificación.
        password es opcional; si es None no se modifica.
        """
        self._dao.actualizarOperador(
            usuario.usuario_id, telefono, estado, password or None
        )
        self._registrar("Modificación", f"Operador editado: {usuario.email}")

    def bloquear_operador(self, usuario):
        """Bloquea la cuenta de un operador y registra la acción."""
        self._dao.bloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta bloqueada: {usuario.email}")

    def desbloquear_operador(self, usuario):
        """Desbloquea la cuenta de un operador y registra la acción."""
        self._dao.desbloquearCuenta(usuario.usuario_id)
        self._registrar("Bloqueo", f"Cuenta desbloqueada: {usuario.email}")

    # ------------------------------------------------------------------ #
    #  Actividad                                                           #
    # ------------------------------------------------------------------ #

    def obtener_actividad(self, tipo_accion=None, limite=200):
        """
        Devuelve filas de Registro_Actividad.
        tipo_accion filtra por tipo; None o 'Todas' devuelve todo.
        """
        return self._dao.obtenerActividad(tipo_accion=tipo_accion, limite=limite)

    # ------------------------------------------------------------------ #
    #  Backup / Sistema                                                    #
    # ------------------------------------------------------------------ #

    def hacer_backup(self, ruta_carpeta):
        """
        Solicita al DAO que ejecute BACKUP DATABASE.
        Si tiene éxito registra la actividad.
        Devuelve (True, nombre_archivo) o (False, mensaje_error).
        """
        exito, resultado = self._dao.hacerBackup(ruta_carpeta)
        if exito:
            self._registrar("Backup", f"Backup generado: {resultado}")
        return exito, resultado