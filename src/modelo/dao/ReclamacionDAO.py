"""
FeedbackDAO.py
==============
Consultas de solo lectura sobre Feedback_Clientes.
El operador puede consultar todos los feedbacks con datos del cliente y paquete.
"""

from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.FeedbackVO import FeedbackVO

_Q_SELECT_TODOS = """
    SELECT
        fc.feedback_id,
        fc.pedido_id,
        pv.cliente_id,
        pv.identificador_unico          AS pedido_ref,
        u.nombre_completo               AS cliente,
        pt.nombre_paquete               AS paquete,
        pt.destino                      AS destino,
        CONVERT(NVARCHAR(10), pv.fecha_pedido, 23) AS fecha_viaje,
        fc.val_general,
        fc.val_trato_operador,
        fc.val_calidad_transporte,
        fc.val_satisfaccion_alojamiento,
        fc.comentarios
    FROM  Feedback_Clientes    fc
    JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
    JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
    JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
    ORDER BY pv.fecha_pedido DESC
"""
_Q_SELECT_POR_ID = """
    SELECT
        fc.feedback_id,
        fc.pedido_id,
        pv.cliente_id,
        pv.identificador_unico,
        u.nombre_completo,
        pt.nombre_paquete,
        pt.destino,
        CONVERT(NVARCHAR(10), pv.fecha_pedido, 23),
        fc.val_general,
        fc.val_trato_operador,
        fc.val_calidad_transporte,
        fc.val_satisfaccion_alojamiento,
        fc.comentarios
    FROM  Feedback_Clientes    fc
    JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
    JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
    JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
    WHERE fc.feedback_id = ?
"""
_Q_SELECT_PAQUETES_CON_FEEDBACK = """
    SELECT DISTINCT pt.nombre_paquete
    FROM  Feedback_Clientes   fc
    JOIN  Pedidos_Viajes      pv ON fc.pedido_id  = pv.pedido_id
    JOIN  Paquetes_Turisticos pt ON pv.paquete_id = pt.paquete_id
    ORDER BY pt.nombre_paquete
"""
# Base para buscar() — se le añade WHERE dinámico
_Q_BASE_BUSCAR = """
    SELECT
        fc.feedback_id,
        fc.pedido_id,
        pv.cliente_id,
        pv.identificador_unico,
        u.nombre_completo,
        pt.nombre_paquete,
        pt.destino,
        CONVERT(NVARCHAR(10), pv.fecha_pedido, 23),
        fc.val_general,
        fc.val_trato_operador,
        fc.val_calidad_transporte,
        fc.val_satisfaccion_alojamiento,
        fc.comentarios
    FROM  Feedback_Clientes    fc
    JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
    JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
    JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
    {where}
    ORDER BY pv.fecha_pedido DESC
"""

class FeedbackDAO(Conexion):

    @staticmethod
    def _row_a_vo(row) -> FeedbackVO:
        # Orden columnas: 0 feedback_id, 1 pedido_id, 2 cliente_id,
        # 3 pedido_ref, 4 cliente, 5 paquete, 6 destino, 7 fecha_viaje,
        # 8 val_general, 9 val_trato_operador, 10 val_calidad_transporte,
        # 11 val_satisfaccion_alojamiento, 12 comentarios
        return FeedbackVO(
            feedback_id                  = row[0],
            pedido_id                    = row[1],
            cliente_id                   = row[2],
            pedido_ref                   = row[3]  or "",
            cliente                      = row[4]  or "",
            paquete                      = row[5]  or "",
            destino                      = row[6]  or "",
            fecha_viaje                  = row[7]  or "",
            val_general                  = row[8],
            val_trato_operador           = row[9],
            val_calidad_transporte       = row[10],
            val_satisfaccion_alojamiento = row[11],
            comentarios                  = row[12] or "",
        )

    def obtener_todos(self) -> list[FeedbackVO]:
        """Devuelve todos los feedbacks como lista de FeedbackVO."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_TODOS)
            return [self._row_a_vo(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_todos: {e}")
            return []

    def obtener_por_id(self, feedback_id: int) -> FeedbackVO | None:
        """Devuelve un FeedbackVO concreto o None."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_POR_ID, [feedback_id])
            row = cursor.fetchone()
            return self._row_a_vo(row) if row else None
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_por_id: {e}")
            return None

    def buscar(self, texto: str = "", paquete: str = "") -> list[FeedbackVO]:
        """Filtra feedbacks por texto libre en cliente/comentarios y/o paquete."""
        try:
            cursor = self.getCursor()
            params = []
            filtros = []

            if texto:
                filtros.append("(u.nombre_completo LIKE ? OR fc.comentarios LIKE ?)")
                params += [f"%{texto}%", f"%{texto}%"]
            if paquete and paquete != "Todos":
                filtros.append("pt.nombre_paquete = ?")
                params.append(paquete)

            where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
            cursor.execute(_Q_BASE_BUSCAR.format(where=where), params)
            return [self._row_a_vo(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en buscar: {e}")
            return []

    def obtener_paquetes_con_feedback(self) -> list[str]:
        """Devuelve lista de nombres de paquetes que tienen feedback (para el filtro)."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_PAQUETES_CON_FEEDBACK)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_paquetes_con_feedback: {e}")
            return []
