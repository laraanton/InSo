"""
AdminDAO.py  –  Acceso a datos del módulo Administrador
=======================================================
Solo responsabilidad: ejecutar SQL y devolver VOs.
Sin lógica de negocio, sin validaciones, sin formateos.

Tablas que gestiona:
    Usuarios            → operadores y todos los usuarios
    Registro_Actividad  → log de acciones del sistema
"""

from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.UsuariosVO import UsuarioVO
from src.modelo.vo.RegistroActividadVO import RegistroActividadVO

# ── Queries ──────────────────────────────────────────────────────────────────

_Q_INSERTAR_OPERADOR = """
    INSERT INTO Usuarios
           (dni_nie, nombre_completo, email, telefono, password_hash,
            tipo_usuario, preferencia, preferencia_accesibilidad)
    VALUES (?, ?, ?, ?, ?, 'Operador', 'General', 'Ninguna')
"""

_Q_ACTUALIZAR_OPERADOR = """
    UPDATE Usuarios
    SET    telefono = ?,
           estado   = ?
    WHERE  usuario_id = ?
"""

_Q_ACTUALIZAR_OPERADOR_CON_PASS = """
    UPDATE Usuarios
    SET    telefono      = ?,
           estado        = ?,
           password_hash = ?
    WHERE  usuario_id = ?
"""

_Q_BLOQUEAR_CUENTA = """
    UPDATE Usuarios
    SET    cuenta_bloqueada = 1
    WHERE  usuario_id = ?
"""

_Q_DESBLOQUEAR_CUENTA = """
    UPDATE Usuarios
    SET    cuenta_bloqueada = 0
    WHERE  usuario_id = ?
"""

_Q_OBTENER_OPERADORES = """
    SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
           tipo_usuario, estado, preferencia, cuenta_bloqueada, fecha_registro
    FROM   Usuarios
    WHERE  tipo_usuario = 'Operador'
    ORDER  BY nombre_completo
"""

_Q_OBTENER_TODOS_USUARIOS = """
    SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
           tipo_usuario, estado, preferencia, cuenta_bloqueada, fecha_registro
    FROM   Usuarios
    ORDER  BY nombre_completo
"""

_Q_BACKUP = """
    BACKUP DATABASE [SoftripDB] TO DISK = ? WITH FORMAT, INIT, STATS = 10
"""

_Q_INSERTAR_ACTIVIDAD = """
    INSERT INTO Registro_Actividad (usuario_id, tipo_accion, detalle, ip)
    VALUES (?, ?, ?, ?)
"""

_Q_OBTENER_ACTIVIDAD = """
    SELECT TOP (?)
           ra.actividad_id,
           ra.fecha,
           u.nombre_completo,
           u.tipo_usuario,
           ra.tipo_accion,
           ra.detalle,
           ra.ip
    FROM   Registro_Actividad ra
    JOIN   Usuarios            u  ON ra.usuario_id = u.usuario_id
    ORDER  BY ra.fecha DESC
"""

_Q_OBTENER_ACTIVIDAD_FILTRADA = """
    SELECT TOP (?)
           ra.actividad_id,
           ra.fecha,
           u.nombre_completo,
           u.tipo_usuario,
           ra.tipo_accion,
           ra.detalle,
           ra.ip
    FROM   Registro_Actividad ra
    JOIN   Usuarios            u  ON ra.usuario_id = u.usuario_id
    WHERE  ra.tipo_accion = ?
    ORDER  BY ra.fecha DESC
"""

# ── DAO ───────────────────────────────────────────────────────────────────────

class AdminDAO(Conexion):

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _row_a_usuario(row) -> UsuarioVO:
        return UsuarioVO(
            usuario_id    = row[0],
            dni_nie       = row[1],
            nombre_completo = row[2],
            email         = row[3],
            telefono      = row[4],
            tipo_usuario  = row[5],
            estado        = row[6],
            preferencia   = row[7],
            cuenta_bloqueada = row[8],
            fecha_registro = row[9],
        )

    @staticmethod
    def _row_a_actividad(row) -> RegistroActividadVO:
        return RegistroActividadVO(
            actividad_id   = row[0],
            fecha          = row[1],
            nombre_usuario = row[2],
            tipo_usuario   = row[3],
            tipo_accion    = row[4],
            detalle        = row[5],
            ip             = row[6],
        )

    # ── OPERADORES ────────────────────────────────────────────────────────────

    def insertar_operador(self, dni_nie: str, nombre_completo: str, email: str,
                          telefono: str, password_hash: str) -> bool:
        """Inserta un usuario con tipo_usuario = 'Operador'. Devuelve True si ok."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INSERTAR_OPERADOR,
                           [dni_nie, nombre_completo, email, telefono, password_hash])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en insertar_operador: {e}")
            return False

    def actualizar_operador(self, usuario_id: int, telefono: str,
                            estado: str, password_hash: str = None) -> bool:
        """Actualiza teléfono y estado. Si se pasa password_hash lo actualiza también."""
        try:
            cursor = self.getCursor()
            if password_hash:
                cursor.execute(_Q_ACTUALIZAR_OPERADOR_CON_PASS,
                               [telefono, estado, password_hash, usuario_id])
            else:
                cursor.execute(_Q_ACTUALIZAR_OPERADOR,
                               [telefono, estado, usuario_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en actualizar_operador: {e}")
            return False

    def bloquear_cuenta(self, usuario_id: int) -> bool:
        """Pone cuenta_bloqueada = 1."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_BLOQUEAR_CUENTA, [usuario_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en bloquear_cuenta: {e}")
            return False

    def desbloquear_cuenta(self, usuario_id: int) -> bool:
        """Pone cuenta_bloqueada = 0."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_DESBLOQUEAR_CUENTA, [usuario_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en desbloquear_cuenta: {e}")
            return False

    def obtener_operadores(self) -> list:
        """Devuelve lista de UsuarioVO con tipo_usuario = 'Operador'."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_OBTENER_OPERADORES)
            return [self._row_a_usuario(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[AdminDAO] Error en obtener_operadores: {e}")
            return []

    def obtener_todos_usuarios(self) -> list:
        """Devuelve lista de UsuarioVO con todos los usuarios."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_OBTENER_TODOS_USUARIOS)
            return [self._row_a_usuario(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[AdminDAO] Error en obtener_todos_usuarios: {e}")
            return []

    # ── BACKUP ────────────────────────────────────────────────────────────────

    def hacer_backup(self, ruta_completa: str) -> bool:
        """
        Ejecuta BACKUP DATABASE en SQL Server hacia ruta_completa.
        Solo ejecuta el SQL, la ruta la construye la Lógica.
        Devuelve True si ok.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_BACKUP, [ruta_completa])
            try:
                while cursor.nextset():
                    pass
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en hacer_backup: {e}")
            return False

    # ── REGISTRO DE ACTIVIDAD ─────────────────────────────────────────────────

    def insertar_actividad(self, usuario_id: int, tipo_accion: str,
                           detalle: str = None, ip: str = None) -> bool:
        """Inserta una fila en Registro_Actividad."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INSERTAR_ACTIVIDAD,
                           [usuario_id, tipo_accion, detalle, ip])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[AdminDAO] Error en insertar_actividad: {e}")
            return False

    def obtener_actividad(self, tipo_accion: str = None,
                          limite: int = 200) -> list:
        """
        Devuelve lista de RegistroActividadVO.
        Si tipo_accion es None o 'Todas' devuelve todos los registros.
        """
        try:
            cursor = self.getCursor()
            if tipo_accion and tipo_accion != "Todas":
                cursor.execute(_Q_OBTENER_ACTIVIDAD_FILTRADA, [limite, tipo_accion])
            else:
                cursor.execute(_Q_OBTENER_ACTIVIDAD, [limite])
            return [self._row_a_actividad(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[AdminDAO] Error en obtener_actividad: {e}")
            return []
