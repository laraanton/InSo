"""
ReclamacionDAO.py
=================
Consultas sobre Reclamaciones.
El operador puede consultar y filtrar todas las reclamaciones.
Solo lectura — el cambio de estado se hace desde aquí también.
"""

from src.modelo.conexion.Conexion import Conexion


class ReclamacionDAO(Conexion):

    def obtener_todas(self) -> list[dict]:
        """
        Devuelve todas las reclamaciones con datos del cliente y paquete.
        """
        try:
            cursor = self.getCursor()
            cursor.execute("""
                SELECT
                    rc.reclamacion_id,
                    rc.identificador_reclamacion  AS ref_reclamacion,
                    pv.identificador_unico        AS ref_pedido,
                    u.nombre_completo             AS cliente,
                    pt.nombre_paquete             AS paquete,
                    rc.categoria,
                    rc.descripcion_incidente,
                    CONVERT(NVARCHAR(10), rc.fecha_incidente, 23)  AS fecha_incidente,
                    CONVERT(NVARCHAR(16), rc.fecha_registro,  120) AS fecha_registro,
                    rc.estado_reclamacion
                FROM  Reclamaciones        rc
                JOIN  Pedidos_Viajes       pv ON rc.pedido_id  = pv.pedido_id
                JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
                JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
                ORDER BY rc.fecha_registro DESC
            """)
            cols = [
                "reclamacion_id", "ref_reclamacion", "ref_pedido", "cliente",
                "paquete", "categoria", "descripcion_incidente",
                "fecha_incidente", "fecha_registro", "estado_reclamacion"
            ]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ReclamacionDAO] Error en obtener_todas: {e}")
            return []

    def buscar(self, texto: str = "", categoria: str = "",
               estado: str = "") -> list[dict]:
        """Filtra reclamaciones por texto, categoría y/o estado."""
        try:
            cursor = self.getCursor()
            params = []
            filtros = []

            if texto:
                filtros.append(
                    "(u.nombre_completo LIKE ? OR rc.descripcion_incidente LIKE ? "
                    "OR pt.nombre_paquete LIKE ?)"
                )
                params += [f"%{texto}%", f"%{texto}%", f"%{texto}%"]
            if categoria and categoria != "Todas":
                filtros.append("rc.categoria = ?")
                params.append(categoria)
            if estado and estado != "Todos":
                filtros.append("rc.estado_reclamacion = ?")
                params.append(estado)

            where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

            cursor.execute(f"""
                SELECT
                    rc.reclamacion_id,
                    rc.identificador_reclamacion,
                    pv.identificador_unico,
                    u.nombre_completo,
                    pt.nombre_paquete,
                    rc.categoria,
                    rc.descripcion_incidente,
                    CONVERT(NVARCHAR(10), rc.fecha_incidente, 23),
                    CONVERT(NVARCHAR(16), rc.fecha_registro,  120),
                    rc.estado_reclamacion
                FROM  Reclamaciones        rc
                JOIN  Pedidos_Viajes       pv ON rc.pedido_id  = pv.pedido_id
                JOIN  Usuarios             u  ON pv.cliente_id = u.usuario_id
                JOIN  Paquetes_Turisticos  pt ON pv.paquete_id = pt.paquete_id
                {where}
                ORDER BY rc.fecha_registro DESC
            """, params)

            cols = [
                "reclamacion_id", "ref_reclamacion", "ref_pedido", "cliente",
                "paquete", "categoria", "descripcion_incidente",
                "fecha_incidente", "fecha_registro", "estado_reclamacion"
            ]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ReclamacionDAO] Error en buscar: {e}")
            return []

    def actualizar_estado(self, reclamacion_id: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de una reclamación."""
        try:
            cursor = self.getCursor()
            cursor.execute("""
                UPDATE Reclamaciones
                SET    estado_reclamacion = ?
                WHERE  reclamacion_id = ?
            """, [nuevo_estado, reclamacion_id])
            return True
        except Exception as e:
            print(f"[ReclamacionDAO] Error en actualizar_estado: {e}")
            return False
