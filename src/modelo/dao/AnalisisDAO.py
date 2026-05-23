"""
AnalisisDAO.py  –  Consultas de análisis y estadísticas de venta
================================================================
Hereda de Conexion.  Solo lectura: no modifica ninguna tabla.

Tablas consultadas:
    Pedidos_Viajes          (pv)
    Paquetes_Turisticos     (pt)
    Feedback_Clientes       (fc)
    Reclamaciones           (rc)
    Clientes_Perfiles       (cp)
    Usuarios                (u)

Esquema real (extraído del CREATE TABLE):
    Feedback_Clientes  → val_trato_operador, val_calidad_transporte,
                         val_satisfaccion_alojamiento, val_general
                         (NO existe columna 'puntuacion')
    Clientes_Perfiles  → PK: usuario_id  (NO existe columna 'perfil_id')
                         perfil_viajero, preferencia_accesibilidad,
                         presupuesto_promedio
"""

from __future__ import annotations
from datetime import date

from src.modelo.conexion.Conexion import Conexion


class AnalisisDAO(Conexion):

    # ════════════════════════════════════════════════════════════════════
    # KPIs  –  cuatro cifras de cabecera
    # ════════════════════════════════════════════════════════════════════

    def kpis_resumen(self, fecha_desde: date | None = None) -> dict:
        """
        Devuelve un único dict con los cuatro KPI de cabecera:

            ingresos_totales    float | None
            total_pedidos       int
            satisfaccion_media  float | None   (media de val_general, escala 1-5)
            total_reclamaciones int

        Tablas: Pedidos_Viajes, Feedback_Clientes, Reclamaciones
        """
        try:
            cursor = self.getCursor()

            # ── Ingresos y pedidos ────────────────────────────────────────
            params1 = []
            where1  = self._where_fecha("fecha_pedido", fecha_desde, params1)
            cursor.execute(f"""
                SELECT SUM(monto_total)  AS ingresos_totales,
                       COUNT(pedido_id)  AS total_pedidos
                FROM   Pedidos_Viajes
                {where1}
            """, params1)
            row_pv = cursor.fetchone()

            # ── Satisfacción media (val_general de Feedback_Clientes) ─────
            # JOIN con Pedidos_Viajes para aplicar el filtro de fecha
            params2 = []
            join2   = "JOIN Pedidos_Viajes pv ON fc.pedido_id = pv.pedido_id"
            where2  = self._where_fecha("pv.fecha_pedido", fecha_desde, params2)
            cursor.execute(f"""
                SELECT AVG(CAST(fc.val_general AS FLOAT))
                FROM   Feedback_Clientes fc
                {join2}
                {where2}
            """, params2)
            row_fc = cursor.fetchone()

            # ── Reclamaciones ─────────────────────────────────────────────
            params3 = []
            join3   = "JOIN Pedidos_Viajes pv ON rc.pedido_id = pv.pedido_id"
            where3  = self._where_fecha("pv.fecha_pedido", fecha_desde, params3)
            cursor.execute(f"""
                SELECT COUNT(rc.reclamacion_id)
                FROM   Reclamaciones rc
                {join3}
                {where3}
            """, params3)
            row_rc = cursor.fetchone()

            return {
                "ingresos_totales":    float(row_pv[0]) if row_pv and row_pv[0] is not None else None,
                "total_pedidos":       int(row_pv[1])   if row_pv and row_pv[1] is not None else 0,
                "satisfaccion_media":  float(row_fc[0]) if row_fc and row_fc[0] is not None else None,
                "total_reclamaciones": int(row_rc[0])   if row_rc and row_rc[0] is not None else 0,
            }
        except Exception as e:
            print(f"[AnalisisDAO] Error en kpis_resumen: {e}")
            return {
                "ingresos_totales": None, "total_pedidos": 0,
                "satisfaccion_media": None, "total_reclamaciones": 0,
            }

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 1  –  Ventas por paquete (barras)
    # Tablas: Pedidos_Viajes JOIN Paquetes_Turisticos
    # ════════════════════════════════════════════════════════════════════

    def ventas_por_paquete(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Número de pedidos agrupado por nombre de paquete, de mayor a menor.

        Retorna: [{"paquete": str, "ventas": int}, ...]
        """
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("pv.fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT   pt.nombre_paquete,
                         COUNT(pv.pedido_id) AS ventas
                FROM     Pedidos_Viajes      pv
                JOIN     Paquetes_Turisticos pt ON pv.paquete_id = pt.paquete_id
                {where}
                GROUP BY pt.nombre_paquete
                ORDER BY ventas DESC
            """, params)

            return [
                {"paquete": row[0] or "Desconocido", "ventas": int(row[1])}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en ventas_por_paquete: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 2  –  Ingresos por mes (línea)
    # Tabla: Pedidos_Viajes.fecha_pedido + monto_total
    # ════════════════════════════════════════════════════════════════════

    def ingresos_por_mes(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Suma de monto_total agrupada por año-mes, orden cronológico.
        Etiqueta abreviada: "Ene", "Feb", …

        Retorna: [{"mes": str, "total": float}, ...]
        """
        _MESES = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
        }
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT   YEAR(fecha_pedido)  AS anio,
                         MONTH(fecha_pedido) AS mes,
                         SUM(monto_total)    AS total
                FROM     Pedidos_Viajes
                {where}
                GROUP BY YEAR(fecha_pedido), MONTH(fecha_pedido)
                ORDER BY anio, mes
            """, params)

            return [
                {
                    "mes":   _MESES.get(int(row[1]), str(row[1])),
                    "total": float(row[2]) if row[2] is not None else 0.0,
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en ingresos_por_mes: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 3  –  Distribución de estados de pedido (tarta)
    # Tabla: Pedidos_Viajes.estado_pedido
    # ════════════════════════════════════════════════════════════════════

    def distribucion_estados(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Cuenta de pedidos por estado_pedido.

        Retorna: [{"estado": str, "cantidad": int}, ...]
        """
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT   estado_pedido,
                         COUNT(*) AS cantidad
                FROM     Pedidos_Viajes
                {where}
                GROUP BY estado_pedido
                ORDER BY cantidad DESC
            """, params)

            return [
                {"estado": row[0] or "Sin estado", "cantidad": int(row[1])}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en distribucion_estados: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 4  –  Satisfacción media por paquete (barras horizontales)
    # Tablas: Feedback_Clientes JOIN Pedidos_Viajes JOIN Paquetes_Turisticos
    # Columnas usadas: val_trato_operador, val_calidad_transporte,
    #                  val_satisfaccion_alojamiento, val_general
    # ════════════════════════════════════════════════════════════════════

    def satisfaccion_por_paquete(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Media de val_general agrupada por nombre de paquete, de mayor a menor.
        Se usa val_general como puntuación global del viaje.

        Retorna: [{"paquete": str, "media": float}, ...]
        """
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("pv.fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT   pt.nombre_paquete,
                         AVG(CAST(fc.val_general AS FLOAT)) AS media
                FROM     Feedback_Clientes     fc
                JOIN     Pedidos_Viajes        pv ON fc.pedido_id  = pv.pedido_id
                JOIN     Paquetes_Turisticos   pt ON pv.paquete_id = pt.paquete_id
                {where}
                GROUP BY pt.nombre_paquete
                ORDER BY media DESC
            """, params)

            return [
                {
                    "paquete": row[0] or "Desconocido",
                    "media":   round(float(row[1]), 2),
                }
                for row in cursor.fetchall()
                if row[1] is not None
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en satisfaccion_por_paquete: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 5  –  Reclamaciones por categoría (barras)
    # Tabla: Reclamaciones.categoria JOIN Pedidos_Viajes (filtro fecha)
    # ════════════════════════════════════════════════════════════════════

    def reclamaciones_por_categoria(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Cuenta de reclamaciones agrupadas por Reclamaciones.categoria.

        Retorna: [{"categoria": str, "cantidad": int}, ...]
        """
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("pv.fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT   rc.categoria,
                         COUNT(rc.reclamacion_id) AS cantidad
                FROM     Reclamaciones  rc
                JOIN     Pedidos_Viajes pv ON rc.pedido_id = pv.pedido_id
                {where}
                GROUP BY rc.categoria
                ORDER BY cantidad DESC
            """, params)

            return [
                {"categoria": row[0] or "Sin categoría", "cantidad": int(row[1])}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en reclamaciones_por_categoria: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Gráfico 6  –  Perfil de viajero más común (tarta)
    # Tabla: Clientes_Perfiles  –  PK: usuario_id  (no perfil_id)
    # Sin filtro de fecha (dato de perfil, no transaccional)
    # ════════════════════════════════════════════════════════════════════

    def distribucion_perfiles(self) -> list[dict]:
        """
        Cuenta de clientes por Clientes_Perfiles.perfil_viajero.
        No filtra por fecha: el perfil es un atributo estático del cliente.

        Retorna: [{"perfil": str, "cantidad": int}, ...]
        """
        try:
            cursor = self.getCursor()
            cursor.execute("""
                SELECT   perfil_viajero,
                         COUNT(usuario_id) AS cantidad
                FROM     Clientes_Perfiles
                GROUP BY perfil_viajero
                ORDER BY cantidad DESC
            """)

            return [
                {"perfil": row[0] or "Sin perfil", "cantidad": int(row[1])}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"[AnalisisDAO] Error en distribucion_perfiles: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Exportación CSV  –  usado por ControladorOperador.exportar_analisis()
    # ════════════════════════════════════════════════════════════════════

    def exportar_resumen(self, fecha_desde: date | None = None) -> list[dict]:
        """
        Una fila por pedido con datos del pedido + valoración + reclamación.

        Columnas de Feedback_Clientes usadas:
            val_trato_operador, val_calidad_transporte,
            val_satisfaccion_alojamiento, val_general

        Retorna: [
            {
                "id_pedido":             str,
                "cliente":               str,
                "paquete":               str,
                "fecha":                 str  (YYYY-MM-DD),
                "monto":                 str  (2 decimales),
                "estado":                str,
                "val_trato":             str,
                "val_transporte":        str,
                "val_alojamiento":       str,
                "val_general":           str,
                "categoria_reclamacion": str,
            },
            ...
        ]
        """
        try:
            cursor = self.getCursor()
            params = []
            where  = self._where_fecha("pv.fecha_pedido", fecha_desde, params)

            cursor.execute(f"""
                SELECT
                    pv.identificador_unico,
                    u.nombre_completo,
                    pt.nombre_paquete,
                    CONVERT(NVARCHAR(10), pv.fecha_pedido, 23) AS fecha,
                    pv.monto_total,
                    pv.estado_pedido,
                    fc.val_trato_operador,
                    fc.val_calidad_transporte,
                    fc.val_satisfaccion_alojamiento,
                    fc.val_general,
                    rc.categoria
                FROM      Pedidos_Viajes       pv
                JOIN      Usuarios             u  ON pv.cliente_id  = u.usuario_id
                JOIN      Paquetes_Turisticos  pt ON pv.paquete_id  = pt.paquete_id
                LEFT JOIN Feedback_Clientes    fc ON fc.pedido_id   = pv.pedido_id
                LEFT JOIN Reclamaciones        rc ON rc.pedido_id   = pv.pedido_id
                {where}
                ORDER BY pv.fecha_pedido DESC
            """, params)

            filas = []
            for row in cursor.fetchall():
                monto = float(row[4]) if row[4] is not None else 0.0
                filas.append({
                    "id_pedido":             row[0]  or "",
                    "cliente":               row[1]  or "",
                    "paquete":               row[2]  or "",
                    "fecha":                 row[3]  or "",
                    "monto":                 f"{monto:.2f}",
                    "estado":                row[5]  or "",
                    "val_trato":             str(row[6])  if row[6]  is not None else "",
                    "val_transporte":        str(row[7])  if row[7]  is not None else "",
                    "val_alojamiento":       str(row[8])  if row[8]  is not None else "",
                    "val_general":           str(row[9])  if row[9]  is not None else "",
                    "categoria_reclamacion": row[10] or "",
                })
            return filas

        except Exception as e:
            print(f"[AnalisisDAO] Error en exportar_resumen: {e}")
            return []

    # ════════════════════════════════════════════════════════════════════
    # Helper privado de filtrado por fecha
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    def _where_fecha(columna: str, fecha_desde: date | None,
                     params: list) -> str:
        """
        Devuelve "WHERE <columna> >= ?" y añade la fecha a params,
        o cadena vacía si fecha_desde es None.

        La columna debe incluir alias de tabla cuando sea necesario
        para evitar ambigüedad en queries con JOINs,
        p.ej. "pv.fecha_pedido" en lugar de solo "fecha_pedido".
        """
        if fecha_desde is None:
            return ""
        params.append(fecha_desde.isoformat())
        return f"WHERE {columna} >= ?"