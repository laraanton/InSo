"""
OperadorBO.py  –  Lógica de negocio del Operador
=================================================
Orquesta los DAOs y construye VOs.
El Controlador NUNCA llama a los DAOs directamente;
siempre pasa por este BO (o por AnalisisBO para los gráficos).

Reglas de negocio aquí:
    - Validación de campos obligatorios del paquete
    - Protección de integridad al eliminar (reservas activas)
    - Validación de estados permitidos en reservas y reclamaciones
    - Registro de historial tras cada mutación
"""

from __future__ import annotations
import csv

from src.modelo.dao.PaqueteDAO     import PaqueteDAO
from src.modelo.dao.ReservaDAO     import ReservaDAO
from src.modelo.dao.FeedbackDAO    import FeedbackDAO
from src.modelo.dao.ReclamacionDAO import ReclamacionDAO

from src.modelo.vo.OperadorVO    import PaqueteVO, ReservaVO, OperacionResultadoVO
from src.modelo.vo.FeedbackVO    import FeedbackVO
from src.modelo.vo.ReclamacionVO import ReclamacionVO


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
        self._usuario_id = usuario_id
        self._paq  = PaqueteDAO()
        self._res  = ReservaDAO()
        self._feed = FeedbackDAO()
        self._rec  = ReclamacionDAO()

    # ── Helpers de conversión dict → VO ──────────────────────────────────────

    @staticmethod
    def _a_paquete_vo(d: dict) -> PaqueteVO:
        return PaqueteVO(
            id          = d.get("id"),
            nombre      = d.get("nombre", ""),
            destino     = d.get("destino", ""),
            duracion    = d.get("duracion"),
            precio      = d.get("precio"),
            servicios   = d.get("servicios", ""),
            descripcion = d.get("descripcion", ""),
            perfil      = d.get("perfil", "General"),
            emoji       = d.get("emoji", "✈️"),
            fecha_ini   = d.get("fecha_ini", ""),
            fecha_fin   = d.get("fecha_fin", ""),
        )

    @staticmethod
    def _a_reserva_vo(d: dict) -> ReservaVO:
        return ReservaVO(
            id                  = d.get("id"),
            identificador_unico = d.get("identificador_unico", ""),
            cliente             = d.get("cliente", ""),
            cliente_id          = d.get("cliente_id"),
            paquete             = d.get("paquete", ""),
            paquete_id          = d.get("paquete_id"),
            fecha               = d.get("fecha", ""),
            precio              = d.get("precio"),
            estado              = d.get("estado", ""),
            metodo_pago         = d.get("metodo_pago", ""),
        )

    @staticmethod
    def _a_feedback_vo(d: dict) -> FeedbackVO:
        return FeedbackVO(
            feedback_id                  = d.get("feedback_id"),
            pedido_ref                   = d.get("pedido_ref", ""),
            cliente                      = d.get("cliente", ""),
            paquete                      = d.get("paquete", ""),
            destino                      = d.get("destino", ""),
            fecha_viaje                  = d.get("fecha_viaje", ""),
            val_trato_operador           = d.get("val_trato_operador"),
            val_calidad_transporte       = d.get("val_calidad_transporte"),
            val_satisfaccion_alojamiento = d.get("val_satisfaccion_alojamiento"),
            val_general                  = d.get("val_general"),
            comentarios                  = d.get("comentarios", ""),
        )

    @staticmethod
    def _a_reclamacion_vo(d: dict) -> ReclamacionVO:
        return ReclamacionVO(
            reclamacion_id        = d.get("reclamacion_id"),
            ref_reclamacion       = d.get("ref_reclamacion", ""),
            ref_pedido            = d.get("ref_pedido", ""),
            cliente               = d.get("cliente", ""),
            paquete               = d.get("paquete", ""),
            categoria             = d.get("categoria", ""),
            descripcion_incidente = d.get("descripcion_incidente", ""),
            fecha_incidente       = d.get("fecha_incidente", ""),
            fecha_registro        = d.get("fecha_registro", ""),
            estado_reclamacion    = d.get("estado_reclamacion", "Registrada"),
        )

    # ── Validación de paquete ─────────────────────────────────────────────────

    @staticmethod
    def _validar_paquete(datos: dict) -> OperacionResultadoVO:
        if not datos.get("nombre", "").strip():
            return OperacionResultadoVO(False, "El campo 'Nombre del paquete' es obligatorio.")
        if not datos.get("destino", "").strip():
            return OperacionResultadoVO(False, "El campo 'Destino' es obligatorio.")
        precio_str = datos.get("precio", "").strip()
        if not precio_str:
            return OperacionResultadoVO(False, "El campo 'Precio' es obligatorio.")
        try:
            if float(precio_str.replace(",", ".")) <= 0:
                raise ValueError
        except ValueError:
            return OperacionResultadoVO(False, "El precio debe ser un número positivo (ej: 1200.00).")
        return OperacionResultadoVO(True, "")

    # ── PAQUETES ──────────────────────────────────────────────────────────────

    def obtener_todos_paquetes(self) -> list[PaqueteVO]:
        return [self._a_paquete_vo(d) for d in self._paq.obtener_todos()]

    def obtener_paquete_por_id(self, id_paquete: int) -> PaqueteVO | None:
        d = self._paq.obtener_por_id(id_paquete)
        return self._a_paquete_vo(d) if d else None

    def crear_paquete(self, datos: dict) -> OperacionResultadoVO:
        resultado = self._validar_paquete(datos)
        if not resultado.ok:
            return resultado
        nuevo_id = self._paq.insertar(datos, operador_id=self._usuario_id)
        if nuevo_id is None:
            return OperacionResultadoVO(False, "Error al guardar el paquete en la base de datos.")
        self._paq.registrar_historial(
            nuevo_id, self._usuario_id,
            f"Paquete '{datos['nombre']}' creado."
        )
        return OperacionResultadoVO(
            True, f"Paquete '{datos['nombre']}' guardado correctamente (ID {nuevo_id})."
        )

    def editar_paquete(self, id_paquete: int, datos: dict) -> OperacionResultadoVO:
        resultado = self._validar_paquete(datos)
        if not resultado.ok:
            return resultado
        if not self._paq.actualizar(id_paquete, datos):
            return OperacionResultadoVO(False, "Error al actualizar el paquete en la base de datos.")
        self._paq.registrar_historial(
            id_paquete, self._usuario_id,
            f"Paquete actualizado: {datos['nombre']}."
        )
        return OperacionResultadoVO(True, f"Paquete '{datos['nombre']}' actualizado correctamente.")

    def eliminar_paquete(self, id_paquete: int) -> OperacionResultadoVO:
        if self._paq.tiene_reservas_activas(id_paquete):
            return OperacionResultadoVO(
                False, "No se puede eliminar: el paquete tiene reservas activas."
            )
        paq = self._paq.obtener_por_id(id_paquete)
        if paq is None:
            return OperacionResultadoVO(False, "Paquete no encontrado.")
        if not self._paq.eliminar(id_paquete):
            return OperacionResultadoVO(False, "Error al eliminar el paquete en la base de datos.")
        self._paq.registrar_historial(
            id_paquete, self._usuario_id,
            f"Paquete '{paq['nombre']}' marcado como Inactivo (eliminado)."
        )
        return OperacionResultadoVO(True, f"Paquete '{paq['nombre']}' eliminado correctamente.")

    # ── RESERVAS ──────────────────────────────────────────────────────────────

    def obtener_reservas(self) -> list[ReservaVO]:
        return [self._a_reserva_vo(d) for d in self._res.obtener_todas()]

    def buscar_reservas(self, texto: str = "", estado: str = "") -> list[ReservaVO]:
        return [self._a_reserva_vo(d)
                for d in self._res.buscar(texto=texto, estado=estado)]

    def cambiar_estado_reserva(self, id_pedido, nuevo_estado: str) -> OperacionResultadoVO:
        if nuevo_estado not in _ESTADOS_RESERVA:
            return OperacionResultadoVO(False, f"Estado '{nuevo_estado}' no reconocido.")
        reserva = self._res.obtener_por_identificador(id_pedido)
        if reserva and reserva.get("estado") == "Finalizado":
            return OperacionResultadoVO(
                False, f"Pedido {id_pedido} ya está finalizado y no se puede modificar."
            )
        ok = self._res.actualizar_estado(id_pedido, nuevo_estado, usuario_id=self._usuario_id)
        if not ok:
            return OperacionResultadoVO(False, f"Pedido {id_pedido} no encontrado o error en BD.")
        return OperacionResultadoVO(True, f"Pedido {id_pedido} → '{nuevo_estado}'.")

    def registrar_reserva(self, datos: dict) -> OperacionResultadoVO:
        if not datos.get("cliente_id"):
            return OperacionResultadoVO(False, "El campo 'cliente_id' es obligatorio.")
        if not datos.get("paquete_id"):
            return OperacionResultadoVO(False, "El campo 'paquete_id' es obligatorio.")
        datos["usuario_responsable"] = self._usuario_id
        identificador = self._res.insertar(datos)
        if identificador is None:
            return OperacionResultadoVO(False, "Error al crear la reserva en la base de datos.")
        return OperacionResultadoVO(True, f"Reserva {identificador} creada correctamente.")

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

    # ── FEEDBACK ──────────────────────────────────────────────────────────────

    def obtener_feedbacks(self) -> list[FeedbackVO]:
        return [self._a_feedback_vo(d) for d in self._feed.obtener_todos()]

    def buscar_feedbacks(self, texto: str = "", paquete: str = "") -> list[FeedbackVO]:
        return [self._a_feedback_vo(d)
                for d in self._feed.buscar(texto=texto, paquete=paquete)]

    def obtener_paquetes_con_feedback(self) -> list[str]:
        return self._feed.obtener_paquetes_con_feedback()

    # ── RECLAMACIONES ─────────────────────────────────────────────────────────

    def obtener_reclamaciones(self) -> list[ReclamacionVO]:
        return [self._a_reclamacion_vo(d) for d in self._rec.obtener_todas()]

    def buscar_reclamaciones(self, texto: str = "", categoria: str = "",
                              estado: str = "") -> list[ReclamacionVO]:
        return [self._a_reclamacion_vo(d)
                for d in self._rec.buscar(texto=texto, categoria=categoria, estado=estado)]

    def cambiar_estado_reclamacion(self, reclamacion_id: int,
                                    nuevo_estado: str) -> OperacionResultadoVO:
        if nuevo_estado not in _ESTADOS_RECLAMACION:
            return OperacionResultadoVO(False, f"Estado '{nuevo_estado}' no reconocido.")
        if not self._rec.actualizar_estado(reclamacion_id, nuevo_estado):
            return OperacionResultadoVO(False, "Error al actualizar el estado en la base de datos.")
        return OperacionResultadoVO(True, f"Estado actualizado a '{nuevo_estado}'.")
