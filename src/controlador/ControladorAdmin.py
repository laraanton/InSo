"""
ControladorAdmin.py  –  Controlador del módulo Administrador
============================================================
    1. Recibe ventana y controlador_principal desde fuera.
    2. Gestiona la navegación con setCurrentIndex.
    3. Delega lógica de negocio en AdminBO.
    4. Devuelve VOs a las subvistas. NUNCA llama a DAOs directamente.
"""

from __future__ import annotations
import importlib

from src.modelo.LogicaAdmin import AdminBO
from src.modelo.vo.UsuariosVO import UsuarioVO
from src.modelo.vo.RegistroActividadVO import RegistroActividadVO
from src.modelo.vo.OperacionResultadoVO import OperacionResultadoVO

# Índices del QStackedWidget — deben coincidir con vistaAdmin.ui
PAG_DASHBOARD  = 0
PAG_OPERADORES = 1
PAG_USUARIOS   = 2
PAG_ACTIVIDAD  = 3
PAG_SISTEMA    = 4

_TITULOS = [
    "Dashboard",
    "Gestión de Operadores",
    "Todos los Usuarios",
    "Registro de Actividad",
    "Sistema y Backups",
]

_BREADCRUMBS = [
    "Softrip › Administración",
    "Softrip › Administración › Operadores",
    "Softrip › Administración › Usuarios",
    "Softrip › Administración › Actividad",
    "Softrip › Administración › Sistema",
]

_MENU_BOTONES = [
    "btnNavDashboard",
    "btnNavOperadores",
    "btnNavUsuarios",
    "btnNavActividad",
    "btnNavSistema",
]


class ControladorAdmin:

    def __init__(self, usuario_actual=None, ventana=None, controlador_principal=None):
        self._usuario_actual  = usuario_actual
        self._ventana         = ventana
        self._ctrl_principal  = controlador_principal
        self._bo              = AdminBO(usuario_actual)

        # Subvistas instanciadas de forma lazy (None hasta que se navega)
        self._widget_dashboard  = None
        self._widget_operadores = None
        self._widget_usuarios   = None
        self._widget_actividad  = None
        self._widget_sistema    = None

    # ── NAVEGACIÓN ────────────────────────────────────────────────────────────

    def navegar_dashboard(self):
        self._ir_a(PAG_DASHBOARD)
        if self._widget_dashboard is None:
            self._widget_dashboard = self._inyectar_subvista(
                "VentanaDashboard_admin", "VentanaDashboard_admin",
                self._ventana.pageDashboard,
                self._ventana.lblDashboardPlaceholder,
            )
            self._widget_dashboard.ir_a_actividad.connect(self.navegar_actividad)

    def navegar_operadores(self):
        self._ir_a(PAG_OPERADORES)
        if self._widget_operadores is None:
            self._widget_operadores = self._inyectar_subvista(
                "VentanaOperadores_admin", "VentanaOperadores_admin",
                self._ventana.pageOperadores,
                self._ventana.lblOperadoresPlaceholder,
            )

    def navegar_usuarios(self):
        self._ir_a(PAG_USUARIOS)
        if self._widget_usuarios is None:
            self._widget_usuarios = self._inyectar_subvista(
                "VentanaUsuarios_admin", "VentanaUsuarios_admin",
                self._ventana.pageUsuarios,
                self._ventana.lblUsuariosPlaceholder,
            )

    def navegar_actividad(self):
        self._ir_a(PAG_ACTIVIDAD)
        if self._widget_actividad is None:
            self._widget_actividad = self._inyectar_subvista(
                "VentanaActividad_admin", "VentanaActividad_admin",
                self._ventana.pageActividad,
                self._ventana.lblActividadPlaceholder,
            )

    def navegar_sistema(self):
        self._ir_a(PAG_SISTEMA)
        if self._widget_sistema is None:
            self._widget_sistema = self._inyectar_subvista(
                "VentanaSistema_admin", "VentanaSistema_admin",
                self._ventana.pageSistema,
                self._ventana.lblSistemaPlaceholder,
            )

    # ── Helpers de navegación ─────────────────────────────────────────────────

    def _ir_a(self, indice: int):
        """Cambia de página y actualiza título, breadcrumb y botones nav.
        Idéntico a ControladorOperador._ir_a."""
        v = self._ventana
        v.stackedWidget.setCurrentIndex(indice)
        v.pageTitle.setText(_TITULOS[indice])
        v.pageBreadcrumb.setText(_BREADCRUMBS[indice])
        for i, nombre in enumerate(_MENU_BOTONES):
            getattr(v, nombre).setChecked(i == indice)

        # Si la subvista ya fue instanciada en una visita anterior, recargar
        widget = self._subvista(indice)
        if widget is not None:
            widget.cargar()

    def _subvista(self, indice: int):
        """Devuelve la subvista ya instanciada para un índice, o None."""
        return {
            PAG_DASHBOARD:  self._widget_dashboard,
            PAG_OPERADORES: self._widget_operadores,
            PAG_USUARIOS:   self._widget_usuarios,
            PAG_ACTIVIDAD:  self._widget_actividad,
            PAG_SISTEMA:    self._widget_sistema,
        }.get(indice)

    def _inyectar_subvista(self, modulo: str, clase: str, page_widget, placeholder):
        """
        Importa la subvista lazy, la instancia con user= y asigna
        controlador= aparte (igual que ControladorOperador).
        El setter controlador de la subvista llama a cargar().
        """
        mod    = importlib.import_module(f"src.vista.{modulo}")
        cls    = getattr(mod, clase)
        widget = cls(user=self._usuario_actual)
        widget.controlador = self                # el setter llama a cargar()

        layout = page_widget.layout()
        layout.removeWidget(placeholder)
        placeholder.hide()
        layout.addWidget(widget)
        return widget

    # ── SESIÓN ────────────────────────────────────────────────────────────────

    def cerrar_sesion(self):
        if self._ctrl_principal:
            self._ctrl_principal.cerrarSesion()

    # ── OPERADORES ────────────────────────────────────────────────────────────

    def obtener_operadores(self) -> list[UsuarioVO]:
        return self._bo.obtener_operadores()

    def crear_operador(self, dni_nie: str, nombre_completo: str,
                       email: str, telefono: str,
                       password: str) -> OperacionResultadoVO:
        return self._bo.crear_operador(dni_nie, nombre_completo, email, telefono, password)

    def actualizar_operador(self, usuario: UsuarioVO, telefono: str,
                            estado: str, password: str = None) -> OperacionResultadoVO:
        return self._bo.actualizar_operador(usuario, telefono, estado, password)

    def bloquear_operador(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        return self._bo.bloquear_operador(usuario)

    def desbloquear_operador(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        return self._bo.desbloquear_operador(usuario)

    # ── USUARIOS ──────────────────────────────────────────────────────────────

    def obtener_todos_usuarios(self) -> list[UsuarioVO]:
        return self._bo.obtener_todos_usuarios()

    def bloquear_cuenta(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        return self._bo.bloquear_cuenta(usuario)

    def desbloquear_cuenta(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        return self._bo.desbloquear_cuenta(usuario)

    # ── BACKUP ────────────────────────────────────────────────────────────────

    def hacer_backup(self, carpeta: str) -> OperacionResultadoVO:
        return self._bo.hacer_backup(carpeta)

    # ── REGISTRO DE ACTIVIDAD ─────────────────────────────────────────────────

    def obtener_actividad(self, tipo_accion: str = None,
                          limite: int = 200) -> list[RegistroActividadVO]:
        return self._bo.obtener_actividad(tipo_accion=tipo_accion, limite=limite)
