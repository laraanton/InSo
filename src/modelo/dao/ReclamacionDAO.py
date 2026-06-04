from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.ReclamacionVO import ReclamacionVO

_Q_SELECT_TODAS = """
    SELECT
        rc.reclamacion_id,
        pv.pedido_id,
        pv.cliente_id,
        pv.identificador_unico AS pedido_ref,
        u.nombre_completo AS cliente,
        pt.nombre_paquete AS paquete,
        pt.destino AS destino,
        CONVERT(NVARCHAR(10), pv.fecha_pedido, 23) AS fecha_pedido,
        rc.categoria AS tipo,
        rc.descripcion_incidente AS descripcion,
        rc.estado_reclamacion AS estado
    FROM Reclamaciones rc
    JOIN Pedidos_Viajes pv ON rc.pedido_id = pv.pedido_id
    JOIN Usuarios u ON pv.cliente_id = u.usuario_id
    JOIN Paquetes_Turisticos pt ON pv.paquete_id = pt.paquete_id
    ORDER BY rc.fecha_registro DESC
"""

_Q_BASE_BUSCAR = """
    SELECT
        rc.reclamacion_id,
        pv.pedido_id,
        pv.cliente_id,
        pv.identificador_unico,
        u.nombre_completo,
        pt.nombre_paquete,
        pt.destino,
        CONVERT(NVARCHAR(10), pv.fecha_pedido, 23),
        rc.categoria,
        rc.descripcion_incidente,
        rc.estado_reclamacion,
        CONVERT(NVARCHAR(16), rc.fecha_registro, 120)
    FROM Reclamaciones rc
    JOIN Pedidos_Viajes pv ON rc.pedido_id = pv.pedido_id
    JOIN Usuarios u ON pv.cliente_id = u.usuario_id
    JOIN Paquetes_Turisticos pt ON pv.paquete_id = pt.paquete_id
    {where}
    ORDER BY rc.fecha_registro DESC
"""
_Q_UPDATE_ESTADO = """
    UPDATE Reclamaciones
    SET    estado_reclamacion = ?
    WHERE  reclamacion_id = ?
"""

class ReclamacionDAO(Conexion):

    @staticmethod
    def _row_a_vo(row) -> ReclamacionVO:
        # Convierte una fila cruda de la BD en un ReclamacionVO
        # Es @staticmethod porque solo transforma datos, no necesita self.
        # Orden columnas: 0 reclamacion_id, 1 pedido_id, 2 cliente_id,
        # 3 pedido_ref, 4 cliente, 5 paquete, 6 destino, 7 fecha_pedido,
        # 8 tipo, 9 descripcion, 10 estado,
        
        return ReclamacionVO(
            reclamacion_id     = row[0],
            pedido_id          = row[1],
            cliente_id         = row[2],
            pedido_ref         = row[3]  or "",
            cliente            = row[4]  or "",
            paquete            = row[5]  or "",
            destino            = row[6]  or "",
            fecha_pedido       = row[7]  or "",
            tipo               = row[8]  or "Otro",
            descripcion        = row[9]  or "",
            estado             = row[10] or "Pendiente",

        )

    def obtener_todas(self) -> list[ReclamacionVO]:
        """Devuelve todas las reclamaciones con datos del cliente y paquete."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_TODAS)
            return [self._row_a_vo(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ReclamacionDAO] Error en obtener_todas: {e}")
            return []

    def buscar(self, texto: str = "", categoria: str = "",
               estado: str = "") -> list[ReclamacionVO]:
        """Filtra reclamaciones por texto, categoría y/o estado."""
        try:
            cursor = self.getCursor()
            params = []
            filtros = []

            if texto:
            # busca el texto en cliente, descripción Y paquete a la vez
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
            
            # si no hay filtros, where queda "" y devuelve todo
            where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
            cursor.execute(_Q_BASE_BUSCAR.format(where=where), params)
            return [self._row_a_vo(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ReclamacionDAO] Error en buscar: {e}")
            return []

    def actualizar_estado(self, reclamacion_id: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de una reclamación. Devuelve True/False para que el BO decida qué mensaje mostrar.
        commit() es obligatorio para persistir el UPDATE en la BD."""
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_UPDATE_ESTADO, [nuevo_estado, reclamacion_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[ReclamacionDAO] Error en actualizar_estado: {e}")
            return False

