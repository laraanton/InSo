import bcrypt
from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.UsuariosVO import UsuarioVO

class UserDAO(Conexion):

    def consultaLogin(self, loginVO):
        try:          
            cursor = self.getCursor()
            cursor.execute(
                """SELECT usuario_id, dni_nie, nombre_completo, email, telefono,
                        tipo_usuario, estado, preferencia, 
                        cuenta_bloqueada, fecha_registro, preferencia_accesibilidad,
                        password_hash
                FROM Usuarios
                WHERE email = ?""",  
                [loginVO.email]
            )
            row = cursor.fetchone()
            if not row:
                return None

            password_hash_guardado = row[-1]  
            print(f"DEBUG hash leído: {repr(password_hash_guardado)}")

            if isinstance(password_hash_guardado, str) and password_hash_guardado.startswith("b'"):
                password_hash_guardado = password_hash_guardado[2:-1]

            password_hash_guardado = password_hash_guardado.encode('utf-8')

            if not bcrypt.checkpw(loginVO.password_hash.encode('utf-8'), password_hash_guardado):
                return None

            return UsuarioVO(*row[:-1])

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
            password_hash = bcrypt.hashpw(
                registroVO.password_hash.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')  #convierte bytes a str limpio
                
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Usuarios 
                (dni_nie, nombre_completo, email, telefono, tipo_usuario, preferencia, preferencia_accesibilidad, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    registroVO.dni_nie, 
                    registroVO.nombre_completo,
                    registroVO.email, 
                    registroVO.telefono,
                    registroVO.tipo_usuario, 
                    registroVO.preferencia, 
                    registroVO.preferencia_accesibilidad,
                    password_hash
                ]
            )
            # Asegura que los cambios se guarden de inmediato en la base de datos
            if hasattr(self, 'commit'): self.commit() 
            return True
        except Exception as e:
            print(f"Error en insertarUsuario: {e}")
            return False

    def actualizarContrasena(self, usuario_id, nueva_contrasena_plana):
        try:
            nuevo_hash = bcrypt.hashpw(
                nueva_contrasena_plana.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')  
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
