"""
LogicaOperador.py  –  Lógica de negocio del Operador
=====================================================
Orquesta los DAOs y aplica reglas de negocio.

Reglas de negocio aquí:
    - Validación de campos obligatorios del paquete
    - Protección de integridad al eliminar (reservas activas)
    - Validación de estados permitidos en reservas y reclamaciones
    - Registro de historial tras cada mutación
"""

from __future__ import annotations
import csv
# Acceso directo a la BD
from src.modelo.dao.PaqueteDAO     import PaqueteDAO
from src.modelo.dao.ReservaDAO     import ReservaDAO
from src.modelo.dao.FeedbackDAO    import FeedbackDAO
from src.modelo.dao.ReclamacionDAO import ReclamacionDAO
# Transferencia de datos entre capas
from src.modelo.vo.PaqueteVO            import PaqueteVO
from src.modelo.vo.ReservaVO            import ReservaVO
from src.modelo.vo.FeedbackVO           import FeedbackVO
from src.modelo.vo.ReclamacionVO        import ReclamacionVO
from src.modelo.vo.OperacionResultadoVO import OperacionResultadoVO


# ── Estados permitidos ────────────────────────────────────────────────────────

_ESTADOS_RESERVA = {
    "Pendiente confirmacion", "Confirmado", "Pagado",
    "En curso", "Finalizado", "Cancelado", "Reembolsado",
}

_ESTADOS_RECLAMACION = {
    "Registrada", "En revisión", "En gestión",
    "Resuelta", "Rechazada", "Cerrada",
}


class OperadorBO:

    def __init__(self, usuario_id=None):
        # ID del operador
        self._usuario_id = usuario_id
        # Instancia cada DAO
        self._paq  = PaqueteDAO()
        self._res  = ReservaDAO()
        self._feed = FeedbackDAO()
        self._rec  = ReclamacionDAO()

    # ── Validación de paquete ─────────────────────────────────────────────

    @staticmethod
    def _validar_paquete(paquete: PaqueteVO) -> OperacionResultadoVO:
        # Comprueba que los campos obligatorios existen y son correctos
        if not (paquete.nombre or "").strip():
            return OperacionResultadoVO(False, "El campo 'Nombre del paquete' es obligatorio.")
        if not (paquete.destino or "").strip():
            return OperacionResultadoVO(False, "El campo 'Destino' es obligatorio.")
        precio_str = str(paquete.precio or "").strip()
        if not precio_str:
            return OperacionResultadoVO(False, "El campo 'Precio' es obligatorio.")
        try:
            if float(precio_str.replace(",", ".")) <= 0:
                raise ValueError
        except ValueError:
            return OperacionResultadoVO(False, "El precio debe ser un número positivo (ej: 1200.00).")
        # Todas las validaciones pasadas: resultado ok sin mensaje de error
        return OperacionResultadoVO(True, "")

    # ── PAQUETES ──────────────────────────────────────────────────────────

    # Devuelve todos los paquetes activos en ls BD
    def obtener_todos_paquetes(self) -> list[PaqueteVO]:
        return self._paq.obtener_todos()

    # Devuelve el paquete con ese ID o None si no existe
    def obtener_paquete_por_id(self, id_paquete: int) -> PaqueteVO | None:
        return self._paq.obtener_por_id(id_paquete)

    # Valida el VO, inserta el paquete y obtiene el nuevo ID asignado
    def crear_paquete(self, paquete: PaqueteVO) -> OperacionResultadoVO:
        resultado = self._validar_paquete(paquete)
        if not resultado.ok:
            return resultado
        nuevo_id = self._paq.insertar(paquete, operador_id=self._usuario_id)
        if nuevo_id is None:
            return OperacionResultadoVO(False, "Error al guardar el paquete en la base de datos.")
        return OperacionResultadoVO(
            True, f"Paquete '{paquete.nombre}' guardado correctamente (ID {nuevo_id})."
        )

    def editar_paquete(self, id_paquete: int, paquete: PaqueteVO) -> OperacionResultadoVO:
        resultado = self._validar_paquete(paquete)
        if not resultado.ok:
            return resultado
        if not self._paq.actualizar(id_paquete, paquete):
            return OperacionResultadoVO(False, "Error al actualizar el paquete en la base de datos.")
        return OperacionResultadoVO(True, f"Paquete '{paquete.nombre}' actualizado correctamente.")

    def eliminar_paquete(self, id_paquete: int) -> OperacionResultadoVO:
        if self._paq.tiene_reservas_activas(id_paquete):
            return OperacionResultadoVO(
                False, "No se puede eliminar: el paquete tiene reservas activas."
            )
        paquete = self._paq.obtener_por_id(id_paquete)
        if paquete is None:
            return OperacionResultadoVO(False, "Paquete no encontrado.")
        if not self._paq.eliminar(id_paquete):
            return OperacionResultadoVO(False, "Error al eliminar el paquete en la base de datos.")
        return OperacionResultadoVO(True, f"Paquete '{paquete.nombre}' eliminado correctamente.")

    # ── RESERVAS ──────────────────────────────────────────────────────────

    # Devuelve toda reserva sin filtro
    def obtener_reservas(self) -> list[ReservaVO]:
        return self._res.obtener_todas()

    def buscar_reservas(self, texto: str = "", estado: str = "") -> list[ReservaVO]:
        return self._res.buscar(texto=texto, estado=estado)

    def cambiar_estado_reserva(self, id_pedido: str, nuevo_estado: str) -> OperacionResultadoVO:
        if nuevo_estado not in _ESTADOS_RESERVA:
            return OperacionResultadoVO(False, f"Estado '{nuevo_estado}' no reconocido.")
        reserva = self._res.obtener_por_identificador(id_pedido)
        if reserva and reserva.estado == "Finalizado":
            return OperacionResultadoVO(
                False, f"Pedido {id_pedido} ya está finalizado y no se puede modificar."
            )
        ok = self._res.actualizar_estado(id_pedido, nuevo_estado, usuario_id=self._usuario_id)
        if not ok:
            return OperacionResultadoVO(False, f"Pedido {id_pedido} no encontrado o error en BD.")
        return OperacionResultadoVO(True, f"Pedido {id_pedido} → '{nuevo_estado}'.")

    def exportar_reservas_csv(self, ruta: str) -> OperacionResultadoVO:
        try:
            reservas = self._res.exportar_todas()
            cabecera = ["ID Pedido", "Cliente", "Paquete", "Fecha", "Precio", "Estado", "Método Pago"]
            campos   = ["id", "cliente", "paquete", "fecha", "precio", "estado", "metodo_pago"]
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                f.write(",".join(cabecera) + "\n")
                csv.DictWriter(f, fieldnames=campos, extrasaction="ignore").writerows(reservas)
            return OperacionResultadoVO(True, f"Exportado correctamente en: {ruta}")
        except Exception as e:
            return OperacionResultadoVO(False, f"Error al exportar: {e}")

    # ── FEEDBACK ──────────────────────────────────────────────────────────

    def obtener_feedbacks(self) -> list[FeedbackVO]:
        return self._feed.obtener_todos()

    def buscar_feedbacks(self, texto: str = "", paquete: str = "") -> list[FeedbackVO]:
        return self._feed.buscar(texto=texto, paquete=paquete)

    def obtener_paquetes_con_feedback(self) -> list[str]:
        return self._feed.obtener_paquetes_con_feedback()

    # ── RECLAMACIONES ─────────────────────────────────────────────────────

    def obtener_reclamaciones(self) -> list[ReclamacionVO]:
        return self._rec.obtener_todas()

    def buscar_reclamaciones(self, texto: str = "", categoria: str = "",
                              estado: str = "") -> list[ReclamacionVO]:
        return self._rec.buscar(texto=texto, categoria=categoria, estado=estado)

    def cambiar_estado_reclamacion(self, reclamacion_id: int,
                                    nuevo_estado: str) -> OperacionResultadoVO:
        if nuevo_estado not in _ESTADOS_RECLAMACION:
            return OperacionResultadoVO(False, f"Estado '{nuevo_estado}' no reconocido.")
        if not self._rec.actualizar_estado(reclamacion_id, nuevo_estado):
            return OperacionResultadoVO(False, "Error al actualizar el estado en la base de datos.")
        return OperacionResultadoVO(True, f"Estado actualizado a '{nuevo_estado}'.")
