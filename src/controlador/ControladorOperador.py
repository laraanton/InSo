"""
ControladorOperador.py  –  Controlador del módulo Operador
===========================================================
Responsabilidades:
    1. Recibir llamadas de VentanaOperador (Vista principal).
    2. Gestionar la navegación entre páginas del QStackedWidget.
    3. Delegar lógica de negocio en OperadorBO y AnalisisBO.
    4. Devolver VOs a la Vista. NUNCA llama a DAOs directamente.

Patrón de navegación:
    VentanaOperador crea este controlador pasándose a sí misma:
        self._ctrl = ControladorOperador(ventana=self)
    Los botones de VentanaOperador solo hacen:
        self._ctrl.navegar_analisis()
    El controlador decide qué página mostrar y si necesita
    instanciar la subvista por primera vez (lazy loading).
"""

from __future__ import annotations

from src.modelo.LogicaOperador import OperadorBO
from src.modelo.LogicaAnalisis import AnalisisBO

from src.modelo.vo.OperacionResultadoVO import  OperacionResultadoVO
from src.modelo.vo.PaqueteVO import PaqueteVO
from src.modelo.vo.ReservaVO import ReservaVO
from src.modelo.vo.AnalisisVO    import AnalisisVO
from src.modelo.vo.FeedbackVO    import FeedbackVO
from src.modelo.vo.ReclamacionVO import ReclamacionVO

# Índices del QStackedWidget (deben coincidir con vistaOperador.ui)
PAG_HUB           = 0
PAG_DISENO        = 1
PAG_COMPRA        = 2
PAG_EDICION       = 3
PAG_ANALISIS      = 4
PAG_FEEDBACK      = 5
PAG_RECLAMACIONES = 6

_TITULOS = [
    "Centro del Operador",
    "Diseño de Paquetes",
    "Gestión de Compra",
    "Edición de Paquetes",
    "Análisis de Venta",
    "Feedback",
    "Reclamaciones",
]

_BREADCRUMBS = [
    "Softrip › Operador",
    "Softrip › Operador › Diseño de Paquetes",
    "Softrip › Operador › Gestión de Compra",
    "Softrip › Operador › Edición de Paquetes",
    "Softrip › Operador › Análisis de Venta",
    "Softrip › Operador › Feedback",
    "Softrip › Operador › Reclamaciones",
]

_NAV_BOTONES = ["btnNav1", "btnNav2", "btnNav3", "btnNav4", "btnNav5", "btnNav6"]


class ControladorOperador:

    def __init__(self, usuario_id=None, ventana=None):
        """
        ventana : VentanaOperador  –  referencia a la vista principal.
                  El controlador la necesita para cambiar de página y
                  para inyectar las subvistas en los QFrame placeholder.
        """
        self._usuario_id  = usuario_id
        self._ventana     = ventana          # VentanaOperador
        self._operador_bo = OperadorBO(usuario_id)
        self._analisis_bo = AnalisisBO()

        # Subvistas instanciadas de forma lazy (None hasta que se navega)
        self._widget_diseno        = None
        self._widget_compra        = None
        self._widget_edicion       = None
        self._widget_analisis      = None
        self._widget_feedback      = None
        self._widget_reclamaciones = None

    
    #  NAVEGACIÓN
    def navegar_hub(self):
        self._ir_a(PAG_HUB)

    def navegar_diseno(self):
        self._ir_a(PAG_DISENO)
        if self._widget_diseno is None:
            self._widget_diseno = self._inyectar_subvista(
                "VentanaDiseno", "VentanaDiseno",
                self._ventana.pageDiseno,
                self._ventana.lblDisenioPlaceholder,
            )

    def navegar_compra(self):
        self._ir_a(PAG_COMPRA)
        if self._widget_compra is None:
            self._widget_compra = self._inyectar_subvista(
                "VentanaCompra", "VentanaCompra",
                self._ventana.pageCompra,
                self._ventana.lblCompraPlaceholder,
            )

    def navegar_edicion(self):
        self._ir_a(PAG_EDICION)
        if self._widget_edicion is None:
            self._widget_edicion = self._inyectar_subvista(
                "VentanaEditar", "VentanaEditar",
                self._ventana.pageEdicion,
                self._ventana.lblEdicionPlaceholder,
            )

    def navegar_analisis(self):
        self._ir_a(PAG_ANALISIS)
        if self._widget_analisis is None:
            self._widget_analisis = self._inyectar_subvista(
                "VentanaAnalisis", "VentanaAnalisis",
                self._ventana.pageAnalisis,
                self._ventana.lblAnalisisPlaceholder,
            )

    def navegar_feedback(self):
        self._ir_a(PAG_FEEDBACK)
        if self._widget_feedback is None:
            self._widget_feedback = self._inyectar_subvista(
                "VentanaFeedback", "VentanaFeedback",
                self._ventana.pageFeedback,
                self._ventana.lblFeedbackPlaceholder,
            )

    def navegar_reclamaciones(self):
        self._ir_a(PAG_RECLAMACIONES)
        if self._widget_reclamaciones is None:
            self._widget_reclamaciones = self._inyectar_subvista(
                "VentanaReclamaciones", "VentanaReclamaciones",
                self._ventana.pageReclamaciones,
                self._ventana.lblReclamacionesPlaceholder,
            )

    # ── Helpers de navegación 

    def _ir_a(self, indice: int):
        """Cambia de página y actualiza título, breadcrumb y botones nav."""
        v = self._ventana
        v.stackedWidget.setCurrentIndex(indice)
        v.pageTitle.setText(_TITULOS[indice])
        v.pageBreadcrumb.setText(_BREADCRUMBS[indice])
        for i, nombre in enumerate(_NAV_BOTONES):
            getattr(v, nombre).setChecked(indice == i + 1)

    def _inyectar_subvista(self, modulo: str, clase: str, page_widget, placeholder):
        """
        Importa la subvista de forma lazy, la instancia pasando el user
        y la inyecta en el QFrame eliminando el placeholder.
        Devuelve la instancia creada.
        """
        import importlib
        mod    = importlib.import_module(f"src.vista.{modulo}")
        cls    = getattr(mod, clase)
        widget = cls(user=self._ventana.user)

        layout = page_widget.layout()
        layout.removeWidget(placeholder)
        placeholder.hide()
        layout.addWidget(widget)
        return widget

    #  PAQUETES

    def obtener_todos(self) -> list[PaqueteVO]:
        return self._operador_bo.obtener_todos_paquetes()

    def obtener_por_id(self, id_paquete: int) -> PaqueteVO | None:
        return self._operador_bo.obtener_paquete_por_id(id_paquete)

    def crear_paquete(self, datos: dict) -> OperacionResultadoVO:
        return self._operador_bo.crear_paquete(PaqueteVO.from_dict(datos))

    def editar_paquete(self, id_paquete: int, datos: dict) -> OperacionResultadoVO:
        return self._operador_bo.editar_paquete(id_paquete, datos)

    def eliminar_paquete(self, id_paquete: int) -> OperacionResultadoVO:
        return self._operador_bo.eliminar_paquete(id_paquete)

    #  RESERVAS
    def obtener_reservas(self) -> list[ReservaVO]:
        return self._operador_bo.obtener_reservas()

    def buscar_reservas(self, texto: str = "", estado: str = "") -> list[ReservaVO]:
        return self._operador_bo.buscar_reservas(texto=texto, estado=estado)

    def cambiar_estado_reserva(self, id_pedido, nuevo_estado: str) -> OperacionResultadoVO:
        return self._operador_bo.cambiar_estado_reserva(id_pedido, nuevo_estado)

    def registrar_reserva(self, datos: dict) -> OperacionResultadoVO:
        return self._operador_bo.registrar_reserva(datos)

    def exportar_csv(self, ruta: str) -> OperacionResultadoVO:
        return self._operador_bo.exportar_reservas_csv(ruta)

    #  ANÁLISIS
    def get_datos_analisis(self, periodo: str) -> AnalisisVO:
        return self._analisis_bo.get_analisis(periodo)

    def exportar_analisis(self, periodo: str) -> OperacionResultadoVO:
        return self._analisis_bo.exportar_analisis(periodo)

    #  FEEDBACK
    def obtener_feedbacks(self) -> list[FeedbackVO]:
        return self._operador_bo.obtener_feedbacks()

    def buscar_feedbacks(self, texto: str = "", paquete: str = "") -> list[FeedbackVO]:
        return self._operador_bo.buscar_feedbacks(texto=texto, paquete=paquete)

    def obtener_paquetes_con_feedback(self) -> list[str]:
        return self._operador_bo.obtener_paquetes_con_feedback()

    #  RECLAMACIONES

    def obtener_reclamaciones(self) -> list[ReclamacionVO]:
        return self._operador_bo.obtener_reclamaciones()

    def buscar_reclamaciones(self, texto: str = "", categoria: str = "",
                              estado: str = "") -> list[ReclamacionVO]:
        return self._operador_bo.buscar_reclamaciones(texto=texto, categoria=categoria, estado=estado)

    def cambiar_estado_reclamacion(self, reclamacion_id: int, nuevo_estado: str) -> OperacionResultadoVO:
        return self._operador_bo.cambiar_estado_reclamacion(reclamacion_id, nuevo_estado)
