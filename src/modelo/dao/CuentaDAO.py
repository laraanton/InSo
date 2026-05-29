from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.UsuariosVO import UsuarioVO

# ── Queries ──────────────────────────────────────────────────────────────────

_Q_UPDATE_TELEFONO = "UPDATE Usuarios SET telefono = ? WHERE usuario_id = ?"
_Q_UPDATE_PREFERENCIA = "UPDATE Usuarios SET preferencia = ? WHERE usuario_id = ?"
_Q_UPDATE_PREFERENCIA_ACCESIBILIDAD = (
    "UPDATE Usuarios SET preferencia_accesibilidad = ? WHERE usuario_id = ?"
)

# ── DAO ───────────────────────────────────────────────────────────────────────

class CuentaDAO(Conexion):

    def actualizarTelefono(self, usuario_id, telefono):
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_UPDATE_TELEFONO, [telefono, usuario_id])
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarTelefono: {e}")
            return False

    def actualizarPreferencia(self, usuario_id, preferencia):
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_UPDATE_PREFERENCIA, [preferencia, usuario_id])
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarPreferencia: {e}")
            return False

    def actualizarPreferenciaAccesibilidad(self, usuario_id, preferencia_accesibilidad):
        try:
            cursor = self.getCursor()
            cursor.execute(
                _Q_UPDATE_PREFERENCIA_ACCESIBILIDAD,
                [preferencia_accesibilidad, usuario_id]
            )
            if hasattr(self, 'commit'): self.commit()
            return True
        except Exception as e:
            print(f"Error en actualizarPreferenciaAccesibilidad: {e}")
            return False