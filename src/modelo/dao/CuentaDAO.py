from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.UsuariosVO import UsuarioVO

class CuentaDAO(Conexion):

    def actualizarTelefono(self, usuario_id, telefono):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET telefono = ? WHERE usuario_id = ?",
                [telefono, usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarTelefono: {e}")
            return False

    def actualizarPreferencia(self, usuario_id, preferencia):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET preferencia = ? WHERE usuario_id = ?",
                [preferencia, usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarPreferencia: {e}")
            return False
            
    def actualizarPreferenciaAccesibilidad(self, usuario_id, preferencia_accesibilidad):
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Usuarios SET preferencia_accesibilidad = ? WHERE usuario_id = ?",
                [preferencia_accesibilidad, usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarPreferenciaAccesibilidad: {e}")
            return False
