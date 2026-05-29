"""
ControladorAdmin.py  –  Controlador del módulo Administrador
============================================================
Responsabilidades:
    1. Recibir llamadas de VentanaAdmin (Vista principal).
    2. Gestionar la navegación entre páginas del QStackedWidget.
    3. Delegar lógica de negocio en AdminBO.
    4. Devolver VOs a la Vista. 
"""

from __future__ import annotations

from src.modelo.LogicaAdmin import AdminBO
from src.modelo.vo.UsuariosVO import UsuarioVO
from src.modelo.vo.RegistroActividadVO import RegistroActividadVO
from src.modelo.vo.OperacionResultadoVO import OperacionResultadoVO

# Índices del QStackedWidget (deben coincidir con vistaAdmin.ui)
PAG_DASHBOARD  = 0
PAG_OPERADORES = 1
PAG_USUARIOS   = 2
PAG_ACTIVIDAD  = 3
PAG_SISTEMA    = 4

_TITULOS = {
    PAG_DASHBOARD:  ("Dashboard",             "Softrip › Administración"),
    PAG_OPERADORES: ("Gestión de Operadores", "Softrip › Administración › Operadores"),
    PAG_USUARIOS:   ("Todos los Usuarios",    "Softrip › Administración › Usuarios"),
    PAG_ACTIVIDAD:  ("Registro de Actividad", "Softrip › Administración › Actividad"),
    PAG_SISTEMA:    ("Sistema y Backups",     "Softrip › Administración › Sistema"),
}


class ControladorAdmin:

    def __init__(self, usuario_actual=None, ventana=None):
        self._usuario_actual = usuario_actual
        self._ventana        = ventana
        self._bo             = AdminBO(usuario_actual)

    # ── NAVEGACIÓN ────────────────────────────────────────────────────────────

    def navegar_dashboard(self):
        self._ir_a(PAG_DASHBOARD)

    def navegar_operadores(self):
        self._ir_a(PAG_OPERADORES)

    def navegar_usuarios(self):
        self._ir_a(PAG_USUARIOS)

    def navegar_actividad(self):
        self._ir_a(PAG_ACTIVIDAD)

    def navegar_sistema(self):
        self._ir_a(PAG_SISTEMA)

    def _ir_a(self, indice: int):
        """Cambia de página, actualiza título, breadcrumb y botón activo."""
        if self._ventana is None:
            return
        self._ventana.stackedWidget.setCurrentWidget(
            self._ventana.paginas[indice]
        )
        titulo, breadcrumb = _TITULOS[indice]
        self._ventana.pageTitle.setText(titulo)
        self._ventana.pageBreadcrumb.setText(breadcrumb)
        # Marca el botón del menú lateral como activo
        self._ventana.marcar_activo(indice)
        # Carga los datos de la subvista
        self._ventana.paginas[indice].cargar()

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
