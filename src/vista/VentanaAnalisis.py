"""
VentanaAnalisis.py  –  Vista de Análisis de Venta
==================================================
Responsabilidad: solicitar datos al ControladorOperador y poblar
los widgets gráficos del .ui. No contiene lógica de negocio ni
acceso directo a la base de datos.

Widgets del .ui que usa esta vista:
    cbPeriodo, btnExportar, lblEstado
    kpiValue1..4                          ← totales KPI
    chartArea1..6                         ← QFrame donde se inyectan
                                            los canvas de Matplotlib
Gráficos y tablas origen:
    1. Ventas por paquete  (barras)   → Pedidos_Viajes + Paquetes_Turisticos
    2. Ingresos por mes    (línea)    → Pedidos_Viajes.fecha_pedido + monto_total
    3. Estado de pedidos   (tarta)    → Pedidos_Viajes.estado_pedido
    4. Satisfacción media  (barras h) → Feedback_Clientes + Pedidos_Viajes
    5. Reclamaciones cat.  (barras)   → Reclamaciones.categoria
    6. Perfil de viajero   (tarta)    → Clientes_Perfiles.perfil_viajero
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Matplotlib integrado en Qt5
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.controlador.ControladorOperador import ControladorOperador

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaAnalisis.ui"
)

_TEAL    = "#5e8d8d"
_TEAL2   = "#7eb8b8"
_TEAL3   = "#4a7474"
_BG      = "#f4f2ed"
_TEXT    = "#333333"
_GRAY    = "#cccccc"
_PALETTE = [_TEAL, _TEAL2, "#a8c8c8", _TEAL3, "#2d5f5f", "#91b8b8"]


class VentanaAnalisis(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user  = user
        self._ctrl = ControladorOperador()
        self._canvases: list[FigureCanvas] = []   # referencia para limpiar

        # "Todo" es el índice 0 → sin filtro de fecha desde el inicio
        self.cbPeriodo.setCurrentIndex(0)

        self._conectar_senales()
        self._cargar_datos()

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.cbPeriodo.currentIndexChanged.connect(self._cargar_datos)
        self.btnExportar.clicked.connect(self._exportar)

    # ── Carga principal ────────────────────────────────────────────────────

    def _cargar_datos(self):
        """Pide los datos al controlador y refresca todos los gráficos."""
        periodo = self.cbPeriodo.currentText()
        self._set_estado("Cargando datos…")

        try:
            datos = self._ctrl.get_datos_analisis(periodo)
        except Exception as exc:
            self._set_estado(f"Error al cargar datos: {exc}", error=True)
            return

        self._poblar_kpis(datos)
        self._poblar_graficos(datos)
        self._set_estado("")

    # ── KPIs ───────────────────────────────────────────────────────────────

    def _poblar_kpis(self, datos: dict):
        """
        datos esperado:
            kpi_ingresos   → str  p.ej. "12 430 €"
            kpi_pedidos    → str  p.ej. "87"
            kpi_satisf     → str  p.ej. "4.2 / 5"
            kpi_reclam     → str  p.ej. "5"
        """
        self.kpiValue1.setText(datos.get("kpi_ingresos", "—"))
        self.kpiValue2.setText(datos.get("kpi_pedidos",  "—"))
        self.kpiValue3.setText(datos.get("kpi_satisf",   "—"))
        self.kpiValue4.setText(datos.get("kpi_reclam",   "—"))

    # ── Gráficos ───────────────────────────────────────────────────────────

    def _poblar_graficos(self, datos: dict):
        self._embed_chart(self.chartArea1, self._fig_ventas_paquete, datos)
        self._embed_chart(self.chartArea2, self._fig_ingresos_mes,   datos)
        self._embed_chart(self.chartArea3, self._fig_estado_pedidos, datos)
        self._embed_chart(self.chartArea4, self._fig_satisfaccion,   datos)
        self._embed_chart(self.chartArea5, self._fig_reclamaciones,  datos)
        self._embed_chart(self.chartArea6, self._fig_perfil_viajero, datos)

    def _embed_chart(self, frame: QWidget, builder, datos: dict):
        """Limpia el QFrame e inyecta el canvas de Matplotlib."""
        if frame.layout() is not None:
            while frame.layout().count():
                child = frame.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            frame.setLayout(QVBoxLayout())

        layout = frame.layout()
        layout.setContentsMargins(4, 4, 4, 4)

        fig    = builder(datos)
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(canvas)
        self._canvases.append(canvas)

    # ── Builders de figuras ────────────────────────────────────────────────

    @staticmethod
    def _base_fig(nrows=1, ncols=1, height=2.4):
        fig = Figure(figsize=(5, height), dpi=96, facecolor=_BG)
        fig.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.18)
        return fig

    def _fig_ventas_paquete(self, datos: dict) -> Figure:
        """
        Barras: unidades vendidas por paquete turístico.
        datos["ventas_paquete"] → list[dict] con claves 'paquete', 'ventas'
        """
        fig = self._base_fig()
        ax  = fig.add_subplot(111)
        filas = datos.get("ventas_paquete", [])
        if filas:
            nombres = [r["paquete"] for r in filas]
            valores = [r["ventas"]  for r in filas]
            bars = ax.bar(nombres, valores, color=_PALETTE[:len(nombres)],
                          width=0.55, zorder=3)
            ax.bar_label(bars, padding=2, fontsize=7, color=_TEXT)
            ax.set_xticks(range(len(nombres)))
            ax.set_xticklabels(nombres, rotation=18, ha="right", fontsize=7)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        self._estilizar_ax(ax, "Ventas por paquete")
        return fig

    def _fig_ingresos_mes(self, datos: dict) -> Figure:
        """
        Línea: ingresos mensuales.
        datos["ingresos_mes"] → list[dict] con claves 'mes', 'total'
        """
        fig = self._base_fig()
        ax  = fig.add_subplot(111)
        filas = datos.get("ingresos_mes", [])
        if filas:
            meses  = [r["mes"]   for r in filas]
            totals = [r["total"] for r in filas]
            ax.plot(meses, totals, color=_TEAL, linewidth=2, marker="o",
                    markersize=4, zorder=3)
            ax.fill_between(meses, totals, alpha=0.12, color=_TEAL)
            ax.set_xticks(range(len(meses)))
            ax.set_xticklabels(meses, rotation=18, ha="right", fontsize=7)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        self._estilizar_ax(ax, "Ingresos por mes (€)")
        return fig

    def _fig_estado_pedidos(self, datos: dict) -> Figure:
        """
        Tarta: distribución de estados de pedido.
        datos["estado_pedidos"] → list[dict] con claves 'estado', 'cantidad'
        """
        fig = Figure(figsize=(4, 2.4), dpi=96, facecolor=_BG)
        ax  = fig.add_subplot(111)
        filas = datos.get("estado_pedidos", [])
        if filas:
            etiquetas = [r["estado"]   for r in filas]
            valores   = [r["cantidad"] for r in filas]
            wedges, texts, autotexts = ax.pie(
                valores, labels=etiquetas, colors=_PALETTE[:len(etiquetas)],
                autopct="%1.0f%%", startangle=90,
                textprops={"fontsize": 7, "color": _TEXT},
                wedgeprops={"linewidth": 1, "edgecolor": "white"}
            )
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color("white")
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        ax.set_title("Estado de pedidos", fontsize=8, color=_TEXT, pad=6)
        fig.tight_layout(pad=0.4)
        return fig

    def _fig_satisfaccion(self, datos: dict) -> Figure:
        """
        Barras horizontales: puntuación media por paquete.
        datos["satisfaccion"] → list[dict] con claves 'paquete', 'media'
        """
        fig = self._base_fig(height=2.4)
        ax  = fig.add_subplot(111)
        filas = datos.get("satisfaccion", [])
        if filas:
            paquetes = [r["paquete"] for r in filas]
            medias   = [r["media"]   for r in filas]
            y    = range(len(paquetes))
            bars = ax.barh(y, medias, color=_TEAL2, height=0.5, zorder=3)
            ax.set_yticks(y)
            ax.set_yticklabels(paquetes, fontsize=7)
            ax.set_xlim(0, 5)
            ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7, color=_TEXT)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        self._estilizar_ax(ax, "Satisfacción media (/ 5)")
        return fig

    def _fig_reclamaciones(self, datos: dict) -> Figure:
        """
        Barras: número de reclamaciones por categoría.
        datos["reclamaciones"] → list[dict] con claves 'categoria', 'cantidad'
        """
        fig = self._base_fig()
        ax  = fig.add_subplot(111)
        filas = datos.get("reclamaciones", [])
        if filas:
            cats = [r["categoria"] for r in filas]
            cnts = [r["cantidad"]  for r in filas]
            bars = ax.bar(cats, cnts, color=_PALETTE[:len(cats)],
                          width=0.55, zorder=3)
            ax.bar_label(bars, padding=2, fontsize=7, color=_TEXT)
            ax.set_xticks(range(len(cats)))
            ax.set_xticklabels(cats, rotation=18, ha="right", fontsize=7)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        self._estilizar_ax(ax, "Reclamaciones por categoría")
        return fig

    def _fig_perfil_viajero(self, datos: dict) -> Figure:
        """
        Tarta: distribución de perfiles de viajero.
        datos["perfil_viajero"] → list[dict] con claves 'perfil', 'cantidad'
        """
        fig = Figure(figsize=(4, 2.4), dpi=96, facecolor=_BG)
        ax  = fig.add_subplot(111)
        filas = datos.get("perfil_viajero", [])
        if filas:
            perfiles   = [r["perfil"]   for r in filas]
            cantidades = [r["cantidad"] for r in filas]
            wedges, texts, autotexts = ax.pie(
                cantidades, labels=perfiles, colors=_PALETTE[:len(perfiles)],
                autopct="%1.0f%%", startangle=140,
                textprops={"fontsize": 7, "color": _TEXT},
                wedgeprops={"linewidth": 1, "edgecolor": "white"}
            )
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color("white")
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    transform=ax.transAxes, color=_GRAY)
        ax.set_title("Perfil de viajero", fontsize=8, color=_TEXT, pad=6)
        fig.tight_layout(pad=0.4)
        return fig

    # ── Helpers visuales ───────────────────────────────────────────────────

    @staticmethod
    def _estilizar_ax(ax, titulo: str):
        ax.set_facecolor(_BG)
        ax.set_title(titulo, fontsize=8, color=_TEXT, pad=6)
        ax.tick_params(colors=_TEXT, labelsize=7)
        ax.yaxis.set_tick_params(labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#dddddd")
        ax.yaxis.grid(True, color="#e8e5de", linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 10px;"
        )

    def _exportar(self):
        """Delega la exportación en el controlador."""
        ok, msg = self._ctrl.exportar_analisis(self.cbPeriodo.currentText())
        self._set_estado(msg, error=not ok)