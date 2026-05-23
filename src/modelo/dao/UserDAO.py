from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.UsuariosVO import UsuarioVO

class UserDAO(Conexion):

    def consultaLogin(self, loginVO):
        try:
            cursor = self.getCursor()
            # Añadida la columna preferencia_accesibilidad que faltaba en el SELECT
            cursor.execute(
                """SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
                          tipo_usuario, estado, preferencia, 
                          cuenta_bloqueada, fecha_registro, preferencia_accesibilidad
                   FROM Usuarios
                   WHERE email = ? AND password_hash = ?""",
                [loginVO.email, loginVO.password_hash]
            )
            row = cursor.fetchone()
            if not row:
                return None
            return UsuarioVO(*row)
        except Exception as e:
            print(f"Error en consultaLogin: {e}")
            return None

    def obtenerUsuarioPorId(self, usuario_id):
        try:
            cursor = self.getCursor()
            cursor.execute(
                """SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
                          tipo_usuario, estado, preferencia, 
                          cuenta_bloqueada, fecha_registro, preferencia_accesibilidad
                   FROM Usuarios WHERE usuario_id = ?""",
                [usuario_id]
            )
            row = cursor.fetchone()
            return UsuarioVO(*row) if row else None
        except Exception as e:
            print(f"Error en obtenerUsuarioPorId: {e}")
            return None

    def obtenerUsuarioPorEmail(self, email):
        try:
            cursor = self.getCursor()
            cursor.execute(
                """SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
                          tipo_usuario, estado, preferencia, 
                          cuenta_bloqueada, fecha_registro, preferencia_accesibilidad
                   FROM Usuarios WHERE email = ?""",
                [email]
            )
            row = cursor.fetchone()
            return UsuarioVO(*row) if row else None
        except Exception as e:
            print(f"Error en obtenerUsuarioPorEmail: {e}")
            return None

    def obtenerTodosLosUsuarios(self):
        try:
            cursor = self.getCursor()
            cursor.execute(
                """SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
                          tipo_usuario, estado, preferencia, 
                          cuenta_bloqueada, fecha_registro, preferencia_accesibilidad
                   FROM Usuarios"""
            )
            rows = cursor.fetchall()
            return [UsuarioVO(*row) for row in rows]
        except Exception as e:
            print(f"Error en obtenerTodosLosUsuarios: {e}")
            return []

    def insertarUsuario(self, registroVO):
        try:
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Usuarios 
                (dni_nie, nombre_completo, email, telefono, tipo_usuario, preferencia, preferencia_accesibilidad, password_hash, )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    registroVO.dni_nie, registroVO.nombre_completo,
                    registroVO.email, registroVO.telefono,
                    registroVO.password_hash, registroVO.tipo_usuario, 
                    registroVO.preferencia, registroVO.preferencia_accesibilidad
                ]
            )
            # Asegura que los cambios se guarden de inmediato en la base de datos
            if hasattr(self, 'commit'): self.commit() 
            return True
        except Exception as e:
            print(f"Error en insertarUsuario: {e}")
            return False

    def actualizarContrasena(self, usuario_id, nuevo_hash):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET password_hash = ? WHERE usuario_id = ?",
                [nuevo_hash, usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarContrasena: {e}")
            return False

    def bloquearCuenta(self, usuario_id):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET cuenta_bloqueada = 1 WHERE usuario_id = ?",
                [usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en bloquearCuenta: {e}")
            return False

    def desbloquearCuenta(self, usuario_id):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET cuenta_bloqueada = 0 WHERE usuario_id = ?",
                [usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en desbloquearCuenta: {e}")
            return False
