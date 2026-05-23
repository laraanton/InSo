"""
FeedbackDAO.py
==============
Consultas de solo lectura sobre Feedback_Clientes.
El operador puede consultar todos los feedbacks con datos del cliente y paquete.
"""

from src.modelo.conexion.Conexion import Conexion


class FeedbackDAO(Conexion):

    def obtener_todos(self) -> list[dict]:
        """
        Devuelve todos los feedbacks con nombre de cliente, paquete y valoraciones.
        """
        try:
            cursor = self.getCursor()
            cursor.execute("""
                SELECT
                    fc.feedback_id,
                    pv.identificador_unico        AS pedido_ref,
                    u.nombre_completo             AS cliente,
                    pt.nombre_paquete             AS paquete,
                    pt.destino                    AS destino,
                    CONVERT(NVARCHAR(10), pv.fecha_pedido, 23) AS fecha_viaje,
                    fc.val_trato_operador,
                    fc.val_calidad_transporte,
                    fc.val_satisfaccion_alojamiento,
                    fc.val_general,
                    fc.comentarios
                FROM  Feedback_Clientes    fc
                JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
                JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
                JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
                ORDER BY pv.fecha_pedido DESC
            """)
            cols = [
                "feedback_id", "pedido_ref", "cliente", "paquete", "destino",
                "fecha_viaje", "val_trato_operador", "val_calidad_transporte",
                "val_satisfaccion_alojamiento", "val_general", "comentarios"
            ]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_todos: {e}")
            return []

    def obtener_por_id(self, feedback_id: int) -> dict | None:
        """Devuelve un feedback concreto o None."""
        try:
            cursor = self.getCursor()
            cursor.execute("""
                SELECT
                    fc.feedback_id,
                    pv.identificador_unico,
                    u.nombre_completo,
                    pt.nombre_paquete,
                    pt.destino,
                    CONVERT(NVARCHAR(10), pv.fecha_pedido, 23),
                    fc.val_trato_operador,
                    fc.val_calidad_transporte,
                    fc.val_satisfaccion_alojamiento,
                    fc.val_general,
                    fc.comentarios
                FROM  Feedback_Clientes    fc
                JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
                JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
                JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
                WHERE fc.feedback_id = ?
            """, [feedback_id])
            row = cursor.fetchone()
            if not row:
                return None
            cols = [
                "feedback_id", "pedido_ref", "cliente", "paquete", "destino",
                "fecha_viaje", "val_trato_operador", "val_calidad_transporte",
                "val_satisfaccion_alojamiento", "val_general", "comentarios"
            ]
            return dict(zip(cols, row))
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_por_id: {e}")
            return None

    def buscar(self, texto: str = "", paquete: str = "") -> list[dict]:
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

            cursor.execute(f"""
                SELECT
                    fc.feedback_id,
                    pv.identificador_unico,
                    u.nombre_completo,
                    pt.nombre_paquete,
                    pt.destino,
                    CONVERT(NVARCHAR(10), pv.fecha_pedido, 23),
                    fc.val_trato_operador,
                    fc.val_calidad_transporte,
                    fc.val_satisfaccion_alojamiento,
                    fc.val_general,
                    fc.comentarios
                FROM  Feedback_Clientes    fc
                JOIN  Pedidos_Viajes       pv ON fc.pedido_id  = pv.pedido_id
                JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
                JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
                {where}
                ORDER BY pv.fecha_pedido DESC
            """, params)

            cols = [
                "feedback_id", "pedido_ref", "cliente", "paquete", "destino",
                "fecha_viaje", "val_trato_operador", "val_calidad_transporte",
                "val_satisfaccion_alojamiento", "val_general", "comentarios"
            ]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en buscar: {e}")
            return []

    def obtener_paquetes_con_feedback(self) -> list[str]:
        """Devuelve lista de nombres de paquetes que tienen feedback (para el filtro)."""
        try:
            cursor = self.getCursor()
            cursor.execute("""
                SELECT DISTINCT pt.nombre_paquete
                FROM  Feedback_Clientes   fc
                JOIN  Pedidos_Viajes      pv ON fc.pedido_id  = pv.pedido_id
                JOIN  Paquetes_Turisticos pt ON pv.paquete_id = pt.paquete_id
                ORDER BY pt.nombre_paquete
            """)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"[FeedbackDAO] Error en obtener_paquetes_con_feedback: {e}")
            return []
