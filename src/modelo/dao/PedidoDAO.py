# src/modelo/dao/PedidoDAO.py
from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.PedidoVO import PedidoVO


class PedidoDAO(Conexion):

    def insertar_pedido(self, vo: PedidoVO) -> int | None:
        """
        Crea un pedido en Pedidos_Viajes.
        Devuelve el pedido_id generado o None si falla.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Pedidos_Viajes
                    (cliente_id, paquete_id, monto_total,
                        metodo_pago, fecha_inicio, fecha_fin,
                        estado_pedido)
                VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')""",
                [
                    vo.cliente_id,
                    vo.paquete_id,
                    vo.monto_total,
                    vo.metodo_pago,
                    str(vo.fecha_inicio),  # datetime.date → "YYYY-MM-DD"
                    str(vo.fecha_fin),
                ]
            )
            cursor.execute("SELECT @@IDENTITY")
            row = cursor.fetchone()
            nuevo_id = int(row[0]) if row and row[0] is not None else None
            self.conexion.commit()
            return nuevo_id
        except Exception as e:
            print(f"[PedidoDAO] Error en insertar_pedido: {e}")
            return None

    def obtener_por_cliente(self, cliente_id: int) -> list[dict]:
        """Devuelve todos los pedidos de un cliente (para VentanaMisViajes)."""
        try:
            cursor = self.getCursor()
            cursor.execute(
                """SELECT pv.pedido_id, pt.nombre_paquete, pt.destino,
                          pv.fecha_inicio, pv.fecha_fin,
                          pv.monto_total, pv.estado_pedido, pv.metodo_pago
                   FROM   Pedidos_Viajes pv
                   JOIN   Paquetes_Turisticos pt ON pt.paquete_id = pv.paquete_id
                   WHERE  pv.cliente_id = ?
                   ORDER  BY pv.pedido_id DESC""",
                [cliente_id]
            )
            cols = ["pedido_id", "nombre", "destino",
                    "fecha_inicio", "fecha_fin",
                    "monto_total", "estado", "metodo_pago"]
            
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        
        except Exception as e:
            print(f"[PedidoDAO] Error en obtener_por_cliente: {e}")
            return []
