"""
ReservaDAO.py  –  Acceso a datos de Pedidos_Viajes (Reservas)
Hereda de Conexion.  Cada operación de escritura actualiza también Historial_Estados_Pedidos -> trazabilidad (Req_26).

Claves de dict que usa ControladorOperador:
    identificador_unico  (computed: 'ORD-N')  → id
    u.nombre_completo                         → cliente
    pt.nombre_paquete                         → paquete
    fecha_pedido                              → fecha   (YYYY-MM-DD)
    monto_total                               → precio  ("1 200,00 EUR")
    estado_pedido                             → estado
    pedido_id                                 → _pedido_id  (uso interno)
"""

from __future__ import annotations
from src.modelo.conexion.Conexion import Conexion

class ReservaDAO(Conexion):
    _SELECT = """
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

    @staticmethod
    def _row_a_dict(row) -> dict:
        monto = row[5] or 0
        return {
            "id":          row[1] or f"ORD-{row[0]}",
            "cliente":     row[2] or "",
            "paquete":     row[3] or "",
            "fecha":       row[4] or "",
            "precio":      f"{monto:,.2f} EUR".replace(",", "X")
                                               .replace(".", ",")
                                               .replace("X", "."),
            "estado":      row[6] or "Pendiente confirmacion",
            "metodo_pago": row[7] or "PayPal",
            # Claves internas (no se exponen en la tabla)
            "_pedido_id":  row[0],
            "_cliente_id": row[8],
            "_paquete_id": row[9],
        }

    def obtener_todas(self) -> list[dict]:
        #Devuelve todas las reservas en fecha descendente. Con nombre de cliente y paquete mediante JOIN (Req_25)
        try:
            cursor = self.getCursor()
            cursor.execute(self._SELECT + "ORDER BY pv.fecha_pedido DESC")
            return [self._row_a_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[ReservaDAO] Error en obtener_todas: {e}")
            return []

    def buscar(self, texto: str = "", estado: str = "") -> list[dict]:
        #Filtra reservas por texto libre (cliente, paquete, id) o estado (Req_23, Req_26)
        try:
            cursor   = self.getCursor()
            conds    = []
            params   = []

            if texto:
                like = f"%{texto}%"
                conds.append(
                    "(u.nombre_completo   LIKE ? "
                    " OR pt.nombre_paquete LIKE ? "
                    " OR pv.identificador_unico LIKE ?)"
                )
                params += [like, like, like]

            if estado and estado not in ("", "Todos los estados"):
                conds.append("pv.estado_pedido = ?")
                params.append(estado)

            where = ("WHERE " + " AND ".join(conds)) if conds else ""
            query = f"{self._SELECT} {where} ORDER BY pv.fecha_pedido DESC"
            cursor.execute(query, params)
            return [self._row_a_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[ReservaDAO] Error en buscar: {e}")
            return []

    def obtener_por_identificador(self, identificador: str) -> dict | None:
        #Devuelve una reserva por su identificador_unico 
        try:
            cursor = self.getCursor()
            cursor.execute(
                self._SELECT + "WHERE pv.identificador_unico = ?",
                [identificador]
            )
            row = cursor.fetchone()
            return self._row_a_dict(row) if row else None
        except Exception as e:
            print(f"[ReservaDAO] Error en obtener_por_identificador: {e}")
            return None

    def insertar(self, datos: dict) -> str | None:
            #ids -> int
            #monto_total* -> float o str
            #metodo_pago -> [str, default 'PayPal']
            #fechas -> str YYYY-MM-DD
        #Crea un nuevo pedido.  Devuelve el identificador_unico ('ORD-N')
        try:
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Pedidos_Viajes
                       (cliente_id, 
                       paquete_id,
                       monto_total,
                       metodo_pago, 
                       estado_pedido,
                       fecha_inicio, 
                       fecha_fin) 
                   VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)""",
                [
                    int(datos["cliente_id"]),
                    int(datos["paquete_id"]),
                    _to_float(datos.get("monto_total", 0)),
                    datos.get("metodo_pago", "PayPal"),
                    datos.get("fecha_inicio") or None,
                    datos.get("fecha_fin") or None,
                ]
            )
            cursor.execute("SELECT @@IDENTITY")
            row = cursor.fetchone()
            if not row or row[0] is None:
                return None
            pedido_id = int(row[0])

            # Registrar primer estado en el historial
            cursor.execute(
                """INSERT INTO Historial_Estados_Pedidos
                       (pedido_id, estado_anterior, estado_nuevo, usuario_responsable)
                   VALUES (?, 'Ninguno', 'Pendiente', ?)""",
                [pedido_id, datos.get("usuario_responsable")]
            )
            self.conexion.commit()
            return f"ORD-{pedido_id}"
        except Exception as e:
            print(f"[ReservaDAO] Error en insertar: {e}")
            #Devuelve None si falla
            return None

    def actualizar_estado(self, identificador: str, nuevo_estado: str,
                          usuario_id: int | None = None) -> bool:
        #Cambia el estado de un pedido y actualiza Historial_Estados_Pedidos (Req_26).
        try:
            cursor = self.getCursor()

            # Resolver pedido_id y estado actual
            cursor.execute(
                """SELECT pedido_id, estado_pedido
                   FROM   Pedidos_Viajes
                   WHERE  identificador_unico = ?""",
                [identificador] #identificador_unico ('ORD-N')/ pedido_id numérico.
            )
            row = cursor.fetchone()
            if not row:
                print(f"[ReservaDAO] Pedido '{identificador}' no encontrado.")
                return False

            pedido_id, estado_anterior = row[0], row[1]

            # Actualizar estado principal
            cursor.execute(
                "UPDATE Pedidos_Viajes "
                "SET    estado_pedido = ? "
                "WHERE  pedido_id     = ?",
                [nuevo_estado, pedido_id]
            )

            # Registrar en historial
            cursor.execute(
                """INSERT INTO Historial_Estados_Pedidos
                       (pedido_id, estado_anterior, estado_nuevo,
                        motivo, usuario_responsable)
                   VALUES (?, ?, ?, NULL, ?)""",
                [pedido_id, estado_anterior, nuevo_estado, usuario_id]
            )
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[ReservaDAO] Error en actualizar_estado: {e}")
            return False

    def exportar_todas(self) -> list[dict]:
        #Devuelve todas las reservas sin claves internas (_*)
        return [
            {k: v for k, v in r.items() if not k.startswith("_")}
            for r in self.obtener_todas()
        ]


#Función auxiliar
def _to_float(valor, defecto: float = 0.0) -> float:
    try:
        return float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        return defecto