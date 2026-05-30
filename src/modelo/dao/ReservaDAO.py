from __future__ import annotations
from src.modelo.conexion.Conexion import Conexion
from src.modelo.vo.ReservaVO import ReservaVO

_SQL_SELECT_BASE = """
    SELECT pv.pedido_id,
           pv.identificador_unico,
           u.nombre_completo,
           pt.nombre_paquete,
           CONVERT(NVARCHAR(10), pv.fecha_pedido, 23) AS fecha_pedido,
           pv.monto_total,
           pv.estado_pedido,
           pv.metodo_pago,
           pv.cliente_id,
           pv.paquete_id
    FROM   Pedidos_Viajes        pv
    JOIN   Usuarios              u  ON pv.cliente_id  = u.usuario_id
    JOIN   Paquetes_Turisticos   pt ON pv.paquete_id  = pt.paquete_id
"""

_SQL_SELECT_TODAS = _SQL_SELECT_BASE + """
    ORDER BY pv.fecha_pedido DESC
"""

_SQL_SELECT_POR_ID = _SQL_SELECT_BASE + """
    WHERE pv.identificador_unico = ?
"""

_SQL_INSERTAR_PEDIDO = """
    INSERT INTO Pedidos_Viajes
           (cliente_id, paquete_id, monto_total, metodo_pago,
            estado_pedido, fecha_inicio, fecha_fin)
    VALUES (?, ?, ?, ?, 'Pendiente confirmacion', ?, ?)
"""

_SQL_GET_IDENTITY = "SELECT @@IDENTITY"

_SQL_INSERTAR_HISTORIAL = """
    INSERT INTO Historial_Estados_Pedidos
           (pedido_id, estado_anterior, estado_nuevo, usuario_responsable)
    VALUES (?, 'Ninguno', 'Pendiente confirmacion', ?)
"""

_SQL_SELECT_ESTADO_ACTUAL = """
    SELECT pedido_id, estado_pedido
    FROM   Pedidos_Viajes
    WHERE  identificador_unico = ?
"""

_SQL_ACTUALIZAR_ESTADO = """
    UPDATE Pedidos_Viajes
    SET    estado_pedido = ?
    WHERE  pedido_id     = ?
"""

_SQL_INSERTAR_HISTORIAL_CAMBIO = """
    INSERT INTO Historial_Estados_Pedidos
           (pedido_id, estado_anterior, estado_nuevo, motivo, usuario_responsable)
    VALUES (?, ?, ?, NULL, ?)
"""


# DAO

class ReservaDAO(Conexion):

    @staticmethod
    def _row_a_vo(row) -> ReservaVO:
        """Convierte una fila de BD en ReservaVO. Único punto de construcción."""
        return ReservaVO(
            id          = row[1] or f"ORD-{row[0]}",
            cliente     = row[2] or "",
            paquete     = row[3] or "",
            fecha       = row[4] or "",
            precio      = float(row[5] or 0),
            estado      = row[6] or "Pendiente confirmacion",
            metodo_pago = row[7] or "PayPal",
            pedido_id   = row[0],
            cliente_id  = row[8],
            paquete_id  = row[9],
        )

    def obtener_todas(self) -> list[ReservaVO]:
        """Devuelve todas las reservas en fecha descendente (Req_25)."""
        try:
            cursor = self.getCursor()
            cursor.execute(_SQL_SELECT_TODAS)
            return [self._row_a_vo(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[ReservaDAO] Error en obtener_todas: {e}")
            return []

    def buscar(self, texto: str = "", estado: str = "") -> list[ReservaVO]:
        """Filtra reservas por texto libre (cliente, paquete, id) o estado (Req_23, Req_26)."""
        try:
            cursor = self.getCursor()
            conds  = []
            params = []

            if texto:
                like = f"%{texto}%"
                conds.append(
                    "(u.nombre_completo         LIKE ? "
                    " OR pt.nombre_paquete      LIKE ? "
                    " OR pv.identificador_unico LIKE ?)"
                )
                params += [like, like, like]

            if estado and estado not in ("", "Todos los estados"):
                conds.append("pv.estado_pedido = ?")
                params.append(estado)

            where = ("WHERE " + " AND ".join(conds)) if conds else ""
            query = f"{_SQL_SELECT_BASE} {where} ORDER BY pv.fecha_pedido DESC"
            cursor.execute(query, params)
            return [self._row_a_vo(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[ReservaDAO] Error en buscar: {e}")
            return []

    def obtener_por_identificador(self, identificador: str) -> ReservaVO | None:
        """Devuelve una reserva por su identificador_unico."""
        try:
            cursor = self.getCursor()
            cursor.execute(_SQL_SELECT_POR_ID, [identificador])
            row = cursor.fetchone()
            return self._row_a_vo(row) if row else None
        except Exception as e:
            print(f"[ReservaDAO] Error en obtener_por_identificador: {e}")
            return None

    def insertar(self, datos: dict) -> str | None:
        """
        Crea un nuevo pedido. Espera un dict con:
            cliente_id, paquete_id, monto_total, metodo_pago,
            fecha_inicio, fecha_fin, usuario_responsable
        Devuelve el identificador_unico ('ORD-N') o None si falla.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                _SQL_INSERTAR_PEDIDO,
                [
                    int(datos["cliente_id"]),
                    int(datos["paquete_id"]),
                    _to_float(datos.get("monto_total", 0)),
                    datos.get("metodo_pago", "PayPal"),
                    datos.get("fecha_inicio") or None,
                    datos.get("fecha_fin")    or None,
                ]
            )
            cursor.execute(_SQL_GET_IDENTITY)
            row = cursor.fetchone()
            if not row or row[0] is None:
                return None
            pedido_id = int(row[0])

            cursor.execute(_SQL_INSERTAR_HISTORIAL, [pedido_id, datos.get("usuario_responsable")])
            self.conexion.commit()
            return f"ORD-{pedido_id}"
        except Exception as e:
            print(f"[ReservaDAO] Error en insertar: {e}")
            return None

    def actualizar_estado(self, identificador: str, nuevo_estado: str,
                          usuario_id: int | None = None) -> bool:
        """Cambia el estado de un pedido y actualiza Historial_Estados_Pedidos (Req_26)."""
        try:
            cursor = self.getCursor()
            cursor.execute(_SQL_SELECT_ESTADO_ACTUAL, [identificador])
            row = cursor.fetchone()
            if not row:
                print(f"[ReservaDAO] Pedido '{identificador}' no encontrado.")
                return False

            pedido_id, estado_anterior = row[0], row[1]

            cursor.execute(_SQL_ACTUALIZAR_ESTADO, [nuevo_estado, pedido_id])
            cursor.execute(_SQL_INSERTAR_HISTORIAL_CAMBIO,
                           [pedido_id, estado_anterior, nuevo_estado, usuario_id])
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[ReservaDAO] Error en actualizar_estado: {e}")
            return False

    def exportar_todas(self) -> list[dict]:
        """
        Devuelve list[dict] exclusivamente para escritura CSV.
        Usa ReservaVO.to_export_dict() como único punto de serialización.
        """
        return [vo.to_export_dict() for vo in self.obtener_todas()]


# Función auxiliar

def _to_float(valor, defecto: float = 0.0) -> float:
    try:
        return float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        return defecto
