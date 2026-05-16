"""
PaqueteDAO.py  –  Acceso a datos de Paquetes_Turisticos
========================================================
Hereda de Conexion y expone CRUD completo sobre la tabla.

Mapeo entre columnas BD  ↔  claves de dict que usa el Controlador:
    paquete_id              → id
    nombre_paquete          → nombre
    descripcion_detallada   → descripcion
    destino                 → destino
    duracion_dias           → duracion   (str, "5")
    precio_tpv              → precio     (str, "1200.00")
    servicios_incluidos     → servicios
    perfil_objetivo         → perfil
    accesibilidad_certificada → accesibilidad  (bool)
    estado_paquete          → estado_paquete

NOTA: La BD no tiene fecha_ini / fecha_fin en Paquetes_Turisticos,
      esas fechas pertenecen a Pedidos_Viajes.  El dict devuelto
      incluye esas claves vacías para compatibilidad con VentanaEditar.
"""

from __future__ import annotations
from src.modelo.conexion.Conexion import Conexion


class PaqueteDAO(Conexion):

    # ── Query base reutilizable ────────────────────────────────────────────
    _SELECT = """
        SELECT paquete_id, nombre_paquete, descripcion_detallada, destino,
               duracion_dias, precio_tpv, servicios_incluidos, perfil_objetivo,
               accesibilidad_certificada, creado_por_operador,
               CONVERT(NVARCHAR(10), fecha_creacion, 23) AS fecha_creacion,
               estado_paquete
        FROM   Paquetes_Turisticos
    """

    # ── Helpers privados ──────────────────────────────────────────────────

    @staticmethod
    def _row_a_dict(row) -> dict:
        """Convierte una fila de cursor al dict que espera ControladorOperador."""
        return {
            "id":              row[0],
            "nombre":          row[1] or "",
            "descripcion":     row[2] or "",
            "destino":         row[3] or "",
            "duracion":        str(row[4]) if row[4] is not None else "",
            "precio":          str(row[5]) if row[5] is not None else "",
            "servicios":       row[6] or "",
            "perfil":          row[7] or "General",
            "accesibilidad":   bool(row[8]),
            "creado_por":      row[9],
            "fecha_creacion":  row[10] or "",
            "estado_paquete":  row[11] or "Activo",
            # Campos sin columna en BD; se dejan vacíos para VentanaEditar
            "fecha_ini":       "",
            "fecha_fin":       "",
        }

    # ── Lecturas ──────────────────────────────────────────────────────────

    def obtener_todos(self) -> list[dict]:
        """
        Devuelve todos los paquetes que NO están en estado 'Inactivo'.
        Usado por VentanaEditar (lista) y VentanaCompra (catálogo).
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                self._SELECT +
                "WHERE  estado_paquete <> 'Inactivo' "
                "ORDER  BY fecha_creacion DESC"
            )
            return [self._row_a_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[PaqueteDAO] Error en obtener_todos: {e}")
            return []

    def obtener_por_id(self, paquete_id: int) -> dict | None:
        """Devuelve un paquete concreto o None si no existe."""
        try:
            cursor = self.getCursor()
            cursor.execute(
                self._SELECT + "WHERE paquete_id = ?",
                [paquete_id]
            )
            row = cursor.fetchone()
            return self._row_a_dict(row) if row else None
        except Exception as e:
            print(f"[PaqueteDAO] Error en obtener_por_id: {e}")
            return None

    def tiene_reservas_activas(self, paquete_id: int) -> bool:
        """
        Devuelve True si el paquete tiene pedidos en estados que impiden
        su eliminación (Req_27 – integridad referencial).
        En caso de error devuelve True como medida de precaución.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                """SELECT COUNT(*)
                   FROM   Pedidos_Viajes
                   WHERE  paquete_id  = ?
                     AND  estado_pedido NOT IN
                          ('Finalizado', 'Cancelado', 'Reembolsado')""",
                [paquete_id]
            )
            row = cursor.fetchone()
            return bool(row and row[0] > 0)
        except Exception as e:
            print(f"[PaqueteDAO] Error en tiene_reservas_activas: {e}")
            return True

    # ── Escrituras ─────────────────────────────────────────────────────────

    def insertar(self, datos: dict, operador_id: int | None = None) -> int | None:
        """
        Inserta un paquete nuevo.
        Devuelve el paquete_id generado por IDENTITY, o None si falla.

        datos esperados (mismas claves que _row_a_dict devuelve):
            nombre*, destino*, duracion, precio*, descripcion,
            servicios, perfil, accesibilidad
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Paquetes_Turisticos
                       (nombre_paquete, descripcion_detallada, destino,
                        duracion_dias, precio_tpv, servicios_incluidos,
                        perfil_objetivo, accesibilidad_certificada,
                        creado_por_operador, estado_paquete)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Activo')""",
                [
                    datos.get("nombre", "").strip(),
                    datos.get("descripcion", "").strip(),
                    datos.get("destino", "").strip(),
                    _to_int(datos.get("duracion")),
                    _to_float(datos.get("precio")),
                    datos.get("servicios", "").strip(),
                    datos.get("perfil", "General").strip(),
                    1 if datos.get("accesibilidad") else 0,
                    operador_id,
                ]
            )
            # @@IDENTITY devuelve el último IDENTITY generado en la sesión
            cursor.execute("SELECT @@IDENTITY")
            row = cursor.fetchone()
            nuevo_id = int(row[0]) if row and row[0] is not None else None
            self.conexion.commit()
            return nuevo_id
        except Exception as e:
            print(f"[PaqueteDAO] Error en insertar: {e}")
            return None

    def actualizar(self, paquete_id: int, datos: dict) -> bool:
        """
        Actualiza los campos editables de un paquete (Req_27).
        No modifica creado_por_operador ni fecha_creacion.
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                """UPDATE Paquetes_Turisticos
                   SET    nombre_paquete          = ?,
                          descripcion_detallada   = ?,
                          destino                 = ?,
                          duracion_dias           = ?,
                          precio_tpv              = ?,
                          servicios_incluidos     = ?,
                          perfil_objetivo         = ?,
                          accesibilidad_certificada = ?
                   WHERE  paquete_id = ?""",
                [
                    datos.get("nombre", "").strip(),
                    datos.get("descripcion", "").strip(),
                    datos.get("destino", "").strip(),
                    _to_int(datos.get("duracion")),
                    _to_float(datos.get("precio")),
                    datos.get("servicios", "").strip(),
                    datos.get("perfil", "General").strip(),
                    1 if datos.get("accesibilidad") else 0,
                    paquete_id,
                ]
            )
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en actualizar: {e}")
            return False

    def eliminar(self, paquete_id: int) -> bool:
        """
        Borrado lógico: cambia estado_paquete → 'Inactivo'.
        Preserva la integridad referencial con Pedidos_Viajes.
        Verificar antes con tiene_reservas_activas().
        """
        try:
            cursor = self.getCursor()
            cursor.execute(
                "UPDATE Paquetes_Turisticos "
                "SET    estado_paquete = 'Inactivo' "
                "WHERE  paquete_id    = ?",
                [paquete_id]
            )
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en eliminar: {e}")
            return False

    def registrar_historial(self, paquete_id: int, usuario_id: int | None,
                            descripcion: str) -> bool:
        """Guarda un registro en Historial_Cambios_Paquetes."""
        try:
            cursor = self.getCursor()
            cursor.execute(
                """INSERT INTO Historial_Cambios_Paquetes
                       (paquete_id, usuario_id, descripcion_cambio)
                   VALUES (?, ?, ?)""",
                [paquete_id, usuario_id, descripcion]
            )
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"[PaqueteDAO] Error en registrar_historial: {e}")
            return False


# ── Funciones auxiliares de conversión ────────────────────────────────────

def _to_int(valor, defecto: int = 1) -> int:
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return defecto


def _to_float(valor, defecto: float = 0.0) -> float:
    try:
        return float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        return defecto
