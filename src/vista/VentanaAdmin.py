import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic

from src.controlador.ControladorAdmin import ControladorAdmin
from src.vista.VentanaDashboard_admin  import VentanaDashboard_admin
from src.vista.VentanaOperadores_admin import VentanaOperadores_admin
from src.vista.VentanaUsuarios_admin   import VentanaUsuarios_admin
from src.vista.VentanaActividad_admin  import VentanaActividad_admin
from src.vista.VentanaSistema_admin    import VentanaSistema_admin

Form, Window = uic.loadUiType("./src/vista/ui/vistaAdmin.ui")

PAGE_DASHBOARD  = 0
PAGE_OPERADORES = 1
PAGE_USUARIOS   = 2
PAGE_ACTIVIDAD  = 3
PAGE_SISTEMA    = 4

_TITULOS = {
    PAGE_DASHBOARD:  ("Dashboard",             "Softrip › Administración"),
    PAGE_OPERADORES: ("Gestión de Operadores", "Softrip › Administración › Operadores"),
    PAGE_USUARIOS:   ("Todos los Usuarios",    "Softrip › Administración › Usuarios"),
    PAGE_ACTIVIDAD:  ("Registro de Actividad", "Softrip › Administración › Actividad"),
    PAGE_SISTEMA:    ("Sistema y Backups",     "Softrip › Administración › Sistema"),
}


class VentanaAdmin(QMainWindow, Form):

    def __init__(self, usuario_actual):
        super().__init__()
        self.setupUi(self)
        self.usuario_actual = usuario_actual

        # El controlador centraliza el acceso al DAO
        self.controlador = ControladorAdmin(usuario_actual)

        self._pages = {
            PAGE_DASHBOARD:  VentanaDashboard_admin(self.controlador),
            PAGE_OPERADORES: VentanaOperadores_admin(self.controlador),
            PAGE_USUARIOS:   VentanaUsuarios_admin(self.controlador),
            PAGE_ACTIVIDAD:  VentanaActividad_admin(self.controlador),
            PAGE_SISTEMA:    VentanaSistema_admin(self.controlador),
        }

        for idx in sorted(self._pages.keys()):
            self.stackedWidget.addWidget(self._pages[idx])

        self._configurar_topbar()
        self._conectar_senales()
        self._navegar(PAGE_DASHBOARD)

    def _configurar_topbar(self):
        nombre  = self.usuario_actual.nombre_completo or "Admin"
        inicial = nombre[0].upper()
        self.avatarLabel.setText(inicial)
        self.adminNameLabel.setText(nombre)

    def _conectar_senales(self):
        self.btnNavDashboard.clicked.connect(lambda: self._navegar(PAGE_DASHBOARD))
        self.btnNavOperadores.clicked.connect(lambda: self._navegar(PAGE_OPERADORES))
        self.btnNavUsuarios.clicked.connect(lambda: self._navegar(PAGE_USUARIOS))
        self.btnNavActividad.clicked.connect(lambda: self._navegar(PAGE_ACTIVIDAD))
        self.btnNavSistema.clicked.connect(lambda: self._navegar(PAGE_SISTEMA))
        self.btnLogout.clicked.connect(self._cerrar_sesion)

        # El dashboard tiene un botón "Ver todos" que salta a actividad
        self._pages[PAGE_DASHBOARD].ir_a_actividad.connect(
            lambda: self._navegar(PAGE_ACTIVIDAD)
        )

    def _navegar(self, pagina):
        self.stackedWidget.setCurrentWidget(self._pages[pagina])
        self.pageTitle.setText(_TITULOS[pagina][0])
        self.pageBreadcrumb.setText(_TITULOS[pagina][1])

        _botones = {
            PAGE_DASHBOARD:  self.btnNavDashboard,
            PAGE_OPERADORES: self.btnNavOperadores,
            PAGE_USUARIOS:   self.btnNavUsuarios,
            PAGE_ACTIVIDAD:  self.btnNavActividad,
            PAGE_SISTEMA:    self.btnNavSistema,
        }
        for p, btn in _botones.items():
            btn.setProperty("active", p == pagina)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self._pages[pagina].cargar()

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