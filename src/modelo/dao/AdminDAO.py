from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.RegistroVO import RegistroVO

# ── Queries ──────────────────────────────────────────────────────────────────

_Q_INSERT_OPERADOR = """
    INSERT INTO Usuarios
       (dni_nie, nombre_completo, email, telefono, password_hash,
        tipo_usuario, preferencia, preferencia_accesibilidad)
    VALUES (?, ?, ?, ?, ?, 'Operador', 'General', 'Ninguna')
"""
_Q_UPDATE_OPERADOR_CON_PASS = """
    UPDATE Usuarios
    SET telefono = ?, estado = ?, password_hash = ?
    WHERE usuario_id = ?
"""
_Q_UPDATE_OPERADOR_SIN_PASS = """
    UPDATE Usuarios
    SET telefono = ?, estado = ?
    WHERE usuario_id = ?
"""
_Q_BLOQUEAR_CUENTA = "UPDATE Usuarios SET cuenta_bloqueada = 1 WHERE usuario_id = ?"
_Q_DESBLOQUEAR_CUENTA = "UPDATE Usuarios SET cuenta_bloqueada = 0 WHERE usuario_id = ?"

_Q_SELECT_OPERADORES = """
    SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
           tipo_usuario, estado, preferencia, cuenta_bloqueada, fecha_registro
    FROM Usuarios
    WHERE tipo_usuario = 'Operador'
"""
_Q_SELECT_TODOS_USUARIOS = """
    SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
           tipo_usuario, estado, preferencia, cuenta_bloqueada, fecha_registro
    FROM Usuarios
"""
_Q_BACKUP_BD = "BACKUP DATABASE [{}] TO DISK = ? WITH FORMAT, INIT, STATS = 10"

_Q_INSERT_ACTIVIDAD = """
    INSERT INTO Registro_Actividad (usuario_id, tipo_accion, detalle, ip)
    VALUES (?, ?, ?, ?)
"""
_Q_SELECT_ACTIVIDAD_FILTRADA = """
    SELECT TOP (?) ra.actividad_id, ra.fecha, u.nombre_completo,
           u.tipo_usuario, ra.tipo_accion, ra.detalle, ra.ip
    FROM Registro_Actividad ra
    JOIN Usuarios u ON ra.usuario_id = u.usuario_id
    WHERE ra.tipo_accion = ?
    ORDER BY ra.fecha DESC
"""
_Q_SELECT_ACTIVIDAD_TODAS = """
    SELECT TOP (?) ra.actividad_id, ra.fecha, u.nombre_completo,
           u.tipo_usuario, ra.tipo_accion, ra.detalle, ra.ip
    FROM Registro_Actividad ra
    JOIN Usuarios u ON ra.usuario_id = u.usuario_id
    ORDER BY ra.fecha DESC
"""

# ── DAO ───────────────────────────────────────────────────────────────────────

class AdminDAO(Conexion):

    def crearOperador(self, dni_nie, nombre_completo, email, telefono, password_hash):
        """Inserta un usuario con tipo_usuario = 'Operador'."""
        try:
            cursor = self.getCursor()
            cursor.execute(
                _Q_INSERT_OPERADOR,
                [dni_nie, nombre_completo, email, telefono, password_hash]
            )
            return True, "Operador creado correctamente"
        except Exception as e:
            print(f"Error en crearOperador: {e}")
            return False, "No se pudo crear el operador. El email o DNI ya existen"

    def actualizarOperador(self, usuario_id, telefono, estado, password_hash=None):
        """Actualiza teléfono y estado de un operador. Si se pasa password_hash lo actualiza también."""
        try:
            cursor = self.getCursor()
            if password_hash:
                cursor.execute(
                    _Q_UPDATE_OPERADOR_CON_PASS,
                    [telefono, estado, password_hash, usuario_id]
                )
            else:
                cursor.execute(
                    _Q_UPDATE_OPERADOR_SIN_PASS,
                    [telefono, estado, usuario_id]
                )
            return True
        except Exception as e:
            print(f"Error en actualizarOperador: {e}")
            return False

    def bloquearCuenta(self, usuario_id):
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_BLOQUEAR_CUENTA, [usuario_id])
            return True
        except Exception as e:
            print(f"Error en bloquearCuenta: {e}")
            return False

    def desbloquearCuenta(self, usuario_id):
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_DESBLOQUEAR_CUENTA, [usuario_id])
            return True
        except Exception as e:
            print(f"Error en desbloquearCuenta: {e}")
            return False

    def obtenerOperadores(self):
        """Devuelve todos los usuarios con tipo_usuario = 'Operador'."""
        try:
            from src.modelo.vo.UsuariosVO import UsuarioVO
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_OPERADORES)
            return [UsuarioVO(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error en obtenerOperadores: {e}")
            return []

    def obtenerTodosLosUsuarios(self):
        try:
            from src.modelo.vo.UsuariosVO import UsuarioVO
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_TODOS_USUARIOS)
            return [UsuarioVO(*row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error en obtenerTodosLosUsuarios: {e}")
            return []

    def hacerBackup(self, ruta_carpeta: str, nombre_bd: str = "SoftripDB"):
        """
        Ejecuta BACKUP DATABASE en SQL Server.
        ruta_carpeta: carpeta accesible por el servidor SQL (ej: 'C:\\Backups\\').
        Devuelve (True, nombre_archivo) o (False, mensaje_error).
        """
        from datetime import datetime
        import os

        ahora          = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"softrip_backup_{ahora}.bak"
        ruta_completa  = os.path.join(ruta_carpeta, nombre_archivo)

        try:
            cursor = self.getCursor()
            cursor.execute(_Q_BACKUP_BD.format(nombre_bd), [ruta_completa])
            try:
                while cursor.nextset():
                    pass
            except Exception:
                pass
            return True, nombre_archivo
        except Exception as e:
            print(f"Error en hacerBackup: {e}")
            return False, str(e)

    def registrarActividad(self, usuario_id: int, tipo_accion: str,
                           detalle: str = None, ip: str = None):
        """Inserta una fila en Registro_Actividad."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INSERT_ACTIVIDAD, [usuario_id, tipo_accion, detalle, ip])
            return True
        except Exception as e:
            print(f"Error en registrarActividad: {e}")
            return False

    def obtenerActividad(self, tipo_accion: str = None, limite: int = 200):
        """
        Devuelve filas de Registro_Actividad unidas con Usuarios.
        Si tipo_accion != None filtra por ese tipo.
        """
        try:
            cursor = self.getCursor()
            if tipo_accion and tipo_accion != "Todas":
                cursor.execute(_Q_SELECT_ACTIVIDAD_FILTRADA, [limite, tipo_accion])
            else:
                cursor.execute(_Q_SELECT_ACTIVIDAD_TODAS, [limite])
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtenerActividad: {e}")
            return []
