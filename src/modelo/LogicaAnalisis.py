"""
AnalisisBO.py  –  Lógica de negocio de Análisis de Venta
=========================================================
Responsabilidad única: obtener datos del AnalisisDAO,
aplicar formato de presentación y devolver un AnalisisVO.

La Vista y el Controlador NO conocen ni AnalisisDAO ni
la lógica de formateo; solo reciben el AnalisisVO ya listo.
"""

from __future__ import annotations
import csv
import os
from datetime import date, timedelta

from src.modelo.dao.AnalisisDAO  import AnalisisDAO
from src.modelo.vo.AnalisisVO    import AnalisisVO, KpiVO
from src.modelo.vo.OperadorVO    import OperacionResultadoVO


class AnalisisBO:

    def __init__(self):
        self._dao = AnalisisDAO()

    # ── API pública ───────────────────────────────────────────────────────────

    def get_analisis(self, periodo: str) -> AnalisisVO:
        """
        Convierte el texto del combo (p.ej. "Últimos 30 días") en una fecha
        real, consulta todos los datos y devuelve un AnalisisVO listo para
        que la Vista lo pinte sin hacer ningún cálculo adicional.
        """
        fecha_desde = self._resolver_fecha_desde(periodo)
        kpis_raw    = self._dao.kpis_resumen(fecha_desde)

        kpis = KpiVO(
            ingresos      = self._fmt_ingresos(kpis_raw.get("ingresos_totales")),
            pedidos       = str(kpis_raw.get("total_pedidos") or 0),
            satisfaccion  = self._fmt_satisfaccion(kpis_raw.get("satisfaccion_media")),
            reclamaciones = str(kpis_raw.get("total_reclamaciones") or 0),
        )

        return AnalisisVO(
            kpis           = kpis,
            ventas_paquete = self._dao.ventas_por_paquete(fecha_desde),
            ingresos_mes   = self._dao.ingresos_por_mes(fecha_desde),
            estado_pedidos = self._dao.distribucion_estados(fecha_desde),
            satisfaccion   = self._dao.satisfaccion_por_paquete(fecha_desde),
            reclamaciones  = self._dao.reclamaciones_por_categoria(fecha_desde),
            perfil_viajero = self._dao.distribucion_perfiles(),  # sin filtro de fecha
        )

    def exportar_analisis(self, periodo: str) -> OperacionResultadoVO:
        """Genera un CSV con el resumen del período en ~/Documents."""
        try:
            fecha_desde = self._resolver_fecha_desde(periodo)
            filas = self._dao.exportar_resumen(fecha_desde)

            if not filas:
                return OperacionResultadoVO(
                    False, "No hay datos para exportar en el período seleccionado."
                )

            slug = (
                periodo.lower()
                .replace(" ", "_")
                .replace("á", "a").replace("é", "e")
                .replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
            nombre_archivo = f"analisis_{slug}_{date.today().isoformat()}.csv"
            ruta = os.path.join(os.path.expanduser("~"), "Documents", nombre_archivo)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)

            cabeceras = [
                "ID Pedido", "Cliente", "Paquete", "Fecha", "Monto (€)", "Estado",
                "Val. Trato Operador", "Val. Transporte",
                "Val. Alojamiento", "Val. General", "Categoría Reclamación",
            ]
            campos = [
                "id_pedido", "cliente", "paquete", "fecha", "monto", "estado",
                "val_trato", "val_transporte", "val_alojamiento", "val_general",
                "categoria_reclamacion",
            ]
            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                f.write(",".join(cabeceras) + "\n")
                csv.DictWriter(f, fieldnames=campos, extrasaction="ignore").writerows(filas)

            return OperacionResultadoVO(True, f"Exportado correctamente en: {ruta}")

        except Exception as exc:
            return OperacionResultadoVO(False, f"Error al exportar: {exc}")

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _resolver_fecha_desde(periodo: str) -> date | None:
        hoy = date.today()
        mapping = {
            "Últimos 30 días": hoy - timedelta(days=30),
            "Últimos 3 meses": hoy - timedelta(days=90),
            "Últimos 6 meses": hoy - timedelta(days=180),
            "Este año":        date(hoy.year, 1, 1),
        }
        return mapping.get(periodo)  # None → "Todo", sin filtro

    @staticmethod
    def _fmt_ingresos(valor) -> str:
        if valor is None:
            return "— €"
        return f"{float(valor):,.0f} €".replace(",", ".")

    @staticmethod
    def _fmt_satisfaccion(valor) -> str:
        if valor is None:
            return "— / 5"
        return f"{float(valor):.1f} / 5"
