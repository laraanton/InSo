from __future__ import annotations
from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.PaqueteVO import PaqueteVO

# ── Queries ──────────────────────────────────────────────────────────────────

_Q_SELECT_BASE = """
    SELECT paquete_id, nombre_paquete, descripcion_detallada, destino,
           duracion_dias, precio_tpv, servicios_incluidos, perfil_objetivo,
           accesibilidad_certificada, creado_por_operador,
           CONVERT(NVARCHAR(10), fecha_creacion, 23) AS fecha_creacion,
           estado_paquete
    FROM   Paquetes_Turisticos
"""
_Q_SELECT_ACTIVOS = (
    _Q_SELECT_BASE
    + "WHERE  estado_paquete <> 'Inactivo' "
    + "ORDER  BY fecha_creacion DESC"
)
_Q_SELECT_POR_ID = _Q_SELECT_BASE + "WHERE paquete_id = ?"

_Q_COUNT_RESERVAS_ACTIVAS = """
    SELECT COUNT(*)
    FROM   Pedidos_Viajes
    WHERE  paquete_id  = ?
      AND  estado_pedido NOT IN ('Finalizado', 'Cancelado', 'Reembolsado')
"""
_Q_INSERT_PAQUETE = """
    INSERT INTO Paquetes_Turisticos
           (nombre_paquete, descripcion_detallada, destino,
            duracion_dias, precio_tpv, servicios_incluidos,
            perfil_objetivo, accesibilidad_certificada,
            creado_por_operador, estado_paquete)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Activo')
"""
_Q_LAST_IDENTITY = "SELECT @@IDENTITY"

_Q_UPDATE_PAQUETE = """
    UPDATE Paquetes_Turisticos
    SET    nombre_paquete = ?,
           descripcion_detallada = ?,
           destino = ?,
           duracion_dias = ?,
           precio_tpv = ?,
           servicios_incluidos = ?,
           perfil_objetivo = ?,
           accesibilidad_certificada = ?
    WHERE  paquete_id = ?
"""
_Q_INACTIVAR_PAQUETE = (
    "UPDATE Paquetes_Turisticos "
    "SET    estado_paquete = 'Inactivo' "
    "WHERE  paquete_id = ?"
)
_Q_INSERT_HISTORIAL = """
    INSERT INTO Historial_Cambios_Paquetes
           (paquete_id, usuario_id, descripcion_cambio)
    VALUES (?, ?, ?)
"""

# ── DAO ───────────────────────────────────────────────────────────────────────

class PaqueteDAO(Conexion):

    def obtener_todos(self) -> list[PaqueteVO]:
        """Devuelve los paquetes no 'Inactivos'. Lo usan VentanaEditar y VentanaCompra."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_ACTIVOS)
            return [PaqueteVO.from_row(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[PaqueteDAO] Error en obtener_todos: {e}")
            return []

    def obtener_por_id(self, paquete_id: int) -> PaqueteVO | None:
        """Devuelve un paquete concreto o None si no existe."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_POR_ID, [paquete_id])
            row = cursor.fetchone()
            return PaqueteVO.from_row(row) if row else None
        except Exception as e:
            print(f"[PaqueteDAO] Error en obtener_por_id: {e}")
            return None

    def tiene_reservas_activas(self, paquete_id: int) -> bool:
        """True si el paquete tiene pedidos en estados que impiden su eliminación (Req_27)."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_COUNT_RESERVAS_ACTIVAS, [paquete_id])
            row = cursor.fetchone()
            return bool(row and row[0] > 0)
        except Exception as e:
            print(f"[PaqueteDAO] Error en tiene_reservas_activas: {e}")
            # Devuelve True como medida de precaución ante cualquier error.
            return True

    def insertar(self, paquete: PaqueteVO, operador_id: int | None = None) -> int | None:
        """
        Inserta un paquete nuevo y devuelve el paquete_id generado por IDENTITY,
        o None si falla.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INSERT_PAQUETE, paquete.to_insert_params(operador_id))
            # @@IDENTITY devuelve el último IDENTITY generado en la sesión
            cursor.execute(_Q_LAST_IDENTITY)
            row = cursor.fetchone()
            nuevo_id = int(row[0]) if row and row[0] is not None else None
            self.conexion.commit()
            return nuevo_id
        except Exception as e:
            print(f"[PaqueteDAO] Error en insertar: {e}")
            return None

    def actualizar(self, paquete_id: int, paquete: PaqueteVO) -> bool:
        """Actualiza los campos editables de un paquete (Req_27).
        No modifica creado_por_operador ni fecha_creacion."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_UPDATE_PAQUETE, paquete.to_update_params(paquete_id))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en actualizar: {e}")
            return False

    def eliminar(self, paquete_id: int) -> bool:
        """Cambia estado_paquete → 'Inactivo'. Preserva integridad referencial con Pedidos_Viajes."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INACTIVAR_PAQUETE, [paquete_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en eliminar: {e}")
            return False

    def registrar_historial(self, paquete_id: int, usuario_id: int | None, descripcion: str) -> bool:
        """Guarda un registro en Historial_Cambios_Paquetes."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_INSERT_HISTORIAL, [paquete_id, usuario_id, descripcion])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en registrar_historial: {e}")
            return False
