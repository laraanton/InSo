"""
VentanaAdmin.py  –  Vista principal del módulo Administrador
============================================================
Responsabilidad: instanciar las subvistas, inyectarlas en el
QStackedWidget y conectar los botones de navegación con el
ControladorAdmin. No contiene lógica de negocio.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic

from src.controlador.ControladorAdmin import (
    ControladorAdmin, PAG_DASHBOARD, PAG_OPERADORES,
    PAG_USUARIOS, PAG_ACTIVIDAD, PAG_SISTEMA
)
from src.vista.VentanaDashboard_admin  import VentanaDashboard_admin
from src.vista.VentanaOperadores_admin import VentanaOperadores_admin
from src.vista.VentanaUsuarios_admin   import VentanaUsuarios_admin
from src.vista.VentanaActividad_admin  import VentanaActividad_admin
from src.vista.VentanaSistema_admin    import VentanaSistema_admin

Form, Window = uic.loadUiType("./src/vista/ui/vistaAdmin.ui")


class VentanaAdmin(QMainWindow, Form):

    def __init__(self, usuario_actual):
        super().__init__()
        self.setupUi(self)
        self.usuario_actual = usuario_actual

        self._ctrl = ControladorAdmin(usuario_actual=usuario_actual, ventana=self)

        self.paginas = {
            PAG_DASHBOARD:  VentanaDashboard_admin(self._ctrl),
            PAG_OPERADORES: VentanaOperadores_admin(self._ctrl),
            PAG_USUARIOS:   VentanaUsuarios_admin(self._ctrl),
            PAG_ACTIVIDAD:  VentanaActividad_admin(self._ctrl),
            PAG_SISTEMA:    VentanaSistema_admin(self._ctrl),
        }

        # Mapa página → botón de navegación (para marcar el activo)
        self._nav_botones = {
            PAG_DASHBOARD:  self.btnNavDashboard,
            PAG_OPERADORES: self.btnNavOperadores,
            PAG_USUARIOS:   self.btnNavUsuarios,
            PAG_ACTIVIDAD:  self.btnNavActividad,
            PAG_SISTEMA:    self.btnNavSistema,
        }

        for idx in sorted(self.paginas.keys()):
            self.stackedWidget.addWidget(self.paginas[idx])

        self._configurar_topbar()
        self._conectar_senales()
        self._ctrl.navegar_dashboard()

    # ── Topbar ────────────────────────────────────────────────────────────────

    def _configurar_topbar(self):
        nombre  = self.usuario_actual.nombre_completo or "Admin"
        inicial = nombre[0].upper()
        self.avatarLabel.setText(inicial)
        self.adminNameLabel.setText(nombre)
        # Forzar border-radius redondeado en el avatar
        self.avatarLabel.setStyleSheet(
            "background-color: #5e8d8d; color: #FFFFFF; border-radius: 18px;"
            "min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px;"
            "font-weight: 700; font-size: 14px; qproperty-alignment: AlignCenter;"
        )

    # ── Marcar botón activo ───────────────────────────────────────────────────

    def marcar_activo(self, pagina: int):
        """Actualiza el estado visual del botón de navegación activo."""
        for pag, btn in self._nav_botones.items():
            btn.setProperty("active", pag == pagina)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Señales ───────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.btnNavDashboard.clicked.connect(self._ctrl.navegar_dashboard)
        self.btnNavOperadores.clicked.connect(self._ctrl.navegar_operadores)
        self.btnNavUsuarios.clicked.connect(self._ctrl.navegar_usuarios)
        self.btnNavActividad.clicked.connect(self._ctrl.navegar_actividad)
        self.btnNavSistema.clicked.connect(self._ctrl.navegar_sistema)
        self.btnLogout.clicked.connect(self._cerrar_sesion)

        self.paginas[PAG_DASHBOARD].ir_a_actividad.connect(
            self._ctrl.navegar_actividad
        )

    # ── Cerrar sesión ─────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Seguro que quieres cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            from src.vista.Login import MiVentana
            self.ventana_login = MiVentana()
            self.ventana_login.show()
            self.close()


if __name__ == "__main__":
    from src.modelo.vo.UsuariosVO import UsuarioVO
    app = QApplication(sys.argv)
    usuario_prueba = UsuarioVO(1, "12345678A", "Admin Softrip", "admin@softrip.es",
                               "600000000", "Administrador", "Activo", "General", False, None)
    ventana = VentanaAdmin(usuario_prueba)
    ventana.show()
    sys.exit(app.exec_())
