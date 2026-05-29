# src/modelo/dao/PedidoDAO.py
from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.PedidoVO import PedidoVO

# ── Queries ──────────────────────────────────────────────────────────────────

_Q_INSERT_PEDIDO = """
    INSERT INTO Pedidos_Viajes
        (cliente_id, paquete_id, monto_total,
         metodo_pago, fecha_inicio, fecha_fin,
         estado_pedido)
    VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
"""
_Q_LAST_IDENTITY = "SELECT @@IDENTITY"

_Q_SELECT_POR_CLIENTE = """
    SELECT pv.pedido_id, pv.paquete_id, pt.nombre_paquete, pt.destino,
           pt.duracion_dias, pt.servicios_incluidos, pt.descripcion_detallada,
           pv.fecha_inicio, pv.fecha_fin,
           pv.monto_total, pv.estado_pedido, pv.metodo_pago
    FROM   Pedidos_Viajes pv
    JOIN   Paquetes_Turisticos pt ON pt.paquete_id = pv.paquete_id
    WHERE  pv.cliente_id = ?
    ORDER  BY pv.pedido_id DESC
"""
_Q_SELECT_POR_PAQUETE = """
    SELECT pv.pedido_id, pv.paquete_id, pt.nombre_paquete, pt.destino,
           pt.duracion_dias, pt.servicios_incluidos, pt.descripcion_detallada,
           pv.fecha_inicio, pv.fecha_fin,
           pv.monto_total, pv.estado_pedido, pv.metodo_pago
    FROM   Pedidos_Viajes pv
    JOIN   Paquetes_Turisticos pt ON pt.paquete_id = pv.paquete_id
    WHERE  pv.pedido_id = ?
"""

_COLS_PEDIDO = [
    "pedido_id", "paquete_id", "nombre", "destino",
    "duracion", "servicios", "descripcion",
    "fecha_inicio", "fecha_fin",
    "monto_total", "estado", "metodo_pago"
]

# ── DAO ───────────────────────────────────────────────────────────────────────

class PedidoDAO(Conexion):

    def insertar_pedido(self, vo: PedidoVO) -> int | None:
        try:
            cursor = self.getCursor()
            cursor.execute(
                _Q_INSERT_PEDIDO,
                [
                    vo.cliente_id,
                    vo.paquete_id,
                    vo.monto_total,
                    vo.metodo_pago,
                    str(vo.fecha_inicio),  # datetime.date → "YYYY-MM-DD"
                    str(vo.fecha_fin),
                ]
            )
            cursor.execute(_Q_LAST_IDENTITY)
            row = cursor.fetchone()
            nuevo_id = int(row[0]) if row and row[0] is not None else None
            self.conexion.commit()
            return nuevo_id
        except Exception as e:
            print(f"[PedidoDAO] Error en insertar_pedido: {e}")
            return None

    def obtener_por_cliente(self, cliente_id: int) -> list[dict]:
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_POR_CLIENTE, [cliente_id])
            return [dict(zip(_COLS_PEDIDO, r)) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[PedidoDAO] Error en obtener_por_cliente: {e}")
            return []

    def obtener_por_paquete(self, pedido_id: int) -> dict | None:
        try:
            cursor = self.getCursor()
            cursor.execute(_Q_SELECT_POR_PAQUETE, [pedido_id])
            row = cursor.fetchone()
            return dict(zip(_COLS_PEDIDO, row)) if row else None
        except Exception as e:
            print(f"[PedidoDAO] Error en obtener_por_id: {e}")
            return None