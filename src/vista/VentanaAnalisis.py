import os
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.modelo.vo.AnalisisVO import AnalisisVO


UI_FILE = os.path.join(os.path.dirname(__file__), "ui", "vistaAnalisis.ui")


class VentanaAnalisis(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)

        self.user = user
        self._controlador = None
        self._canvases = []

        #periodo por defecto
        self.cbPeriodo.setCurrentIndex(0)

        self.cbPeriodo.currentIndexChanged.connect(self._cargar_datos)
        self.btnExportar.clicked.connect(self._exportar)

    
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self._cargar_datos()

    def _cargar_datos(self):
        #obtiene los datos del VO desde el controlador
        periodo = self.cbPeriodo.currentText()
        self._set_estado("Cargando...")

        try:
            datos: AnalisisVO = self._controlador.get_datos_analisis(periodo)
        except Exception as e:
            self._set_estado(f"Error: {e}", True)
            return

        self._pintar_kpis(datos)
        self._pintar_graficos(datos)
        self._set_estado("")


    def _pintar_kpis(self, d: AnalisisVO):
        # Actualiza indicadores
        k = d.kpis
        self.kpiValue1.setText(k.ingresos if k else "—")
        self.kpiValue2.setText(k.pedidos if k else "—")
        self.kpiValue3.setText(k.satisfaccion if k else "—")
        self.kpiValue4.setText(k.reclamaciones if k else "—")

  
    def _pintar_graficos(self, d: AnalisisVO):
        # Redibuja todos los gráficos
        self._graf(self.chartArea1, self._fig_ventas, d)
        self._graf(self.chartArea2, self._fig_ingresos, d)
        self._graf(self.chartArea3, self._fig_estado, d)
        self._graf(self.chartArea4, self._fig_satisfaccion, d)
        self._graf(self.chartArea5, self._fig_reclamaciones, d)
        self._graf(self.chartArea6, self._fig_perfil, d)

    def _graf(self, frame, builder, datos):
        # Crea layout si no existe

        if not frame.layout():
            frame.setLayout(QVBoxLayout())
        
        lay = frame.layout()
        # Elimina gráfico anterior
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        #nueva figura
        fig = builder(datos)
        canvas = FigureCanvas(fig)

        #inserta figura en el contenedor
        frame.layout().addWidget(canvas)
        self._canvases.append(canvas)

   
    def _fig_ventas(self, d):
        # Gráfico de ventas por paquete
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.ventas_paquete or []
        if data:
            ax.bar([x["paquete"] for x in data],
                   [x["ventas"] for x in data])
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center")
        ax.tick_params(axis='both', labelsize=4)
        return fig

    def _fig_ingresos(self, d):
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.ingresos_mes or []
        if data:
            y = [x["total"] for x in data]
            x = range(len(y))

            ax.plot(x, y, marker="o")

            if len(y) > 1:
                coef = np.polyfit(x, y, 1)
                ax.plot(x, np.poly1d(coef)(x), "--")
        ax.tick_params(axis='both', labelsize=6)

        return fig

    def _fig_estado(self, d):
        """Grafico de tarta de estado de los pedidos"""
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.estado_pedidos or []
        if data:
            ax.pie([x["cantidad"] for x in data],
                   labels=[x["estado"] for x in data])
        
        ax.tick_params(axis='both', labelsize=8)

        return fig

    def _fig_satisfaccion(self, d):
        """Barras horizontales de satisfacción media por paquete """
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.satisfaccion or []
        if data:
            ax.barh([x["paquete"] for x in data],
                    [x["media"] for x in data])
        ax.tick_params(axis='both', labelsize=6)

        return fig

    def _fig_reclamaciones(self, d):
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.reclamaciones or []
        if data:
            ax.bar([x["categoria"] for x in data],
                   [x["cantidad"] for x in data])
        ax.tick_params(axis='both', labelsize=6)
        return fig

    def _fig_perfil(self, d):
        fig = Figure()
        ax = fig.add_subplot(111)

        data = d.perfil_viajero or []
        if data:
            ax.barh([x["perfil"] for x in data],
                    [x["media_presupuesto"] for x in data])
        ax.tick_params(axis='both', labelsize=6)
        return fig

    def _set_estado(self, msg, error=False):
        self.lblEstado.setText(msg)
        self.lblEstado.setStyleSheet(
            f"color: {'#e05252' if error else '#5e8d8d'};"
        )
 
    def _exportar(self):
        r = self._controlador.exportar_analisis(self.cbPeriodo.currentText())
        self._set_estado(r.mensaje, not r.ok)
