import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaOperador.ui"
)

PAG_HUB     = 0
PAG_DISENO  = 1
PAG_COMPRA  = 2
PAG_EDICION = 3

_TITULOS = [
    "Centro del Operador",
    "Diseno de Paquetes",
    "Gestion de Compra",
    "Edicion de Paquetes",
]
_BREADCRUMBS = [
    "Softrip › Operador",
    "Softrip › Operador › Diseno de Paquetes",
    "Softrip › Operador › Gestion de Compra",
    "Softrip › Operador › Edicion de Paquetes",
]
_NAV_BOTONES = ["btnNav1", "btnNav2", "btnNav3"]


class VentanaOperador(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)

        self.user = user

        nombre = user.nombre_completo if user else "Operador"
        self.userNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "O")

        # Referencias a widgets de sección, se crean solo una vez (lazy)
        self._widget_diseno  = None
        self._widget_compra  = None
        self._widget_edicion = None

        self._conectar_senales()
        self._navegar(PAG_HUB)

    def _conectar_senales(self):
        self.logoBtn.clicked.connect(lambda: self._navegar(PAG_HUB))

        self.moreBtn1.clicked.connect(lambda: self._navegar(PAG_DISENO))
        self.moreBtn2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.moreBtn3.clicked.connect(lambda: self._navegar(PAG_EDICION))

        self.btnNav1.clicked.connect(lambda: self._navegar(PAG_DISENO))
        self.btnNav2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.btnNav3.clicked.connect(lambda: self._navegar(PAG_EDICION))

        self.btnLogout.clicked.connect(self._cerrar_sesion)

    def _navegar(self, indice: int):
        self.stackedWidget.setCurrentIndex(indice)
        self.pageTitle.setText(_TITULOS[indice])
        self.pageBreadcrumb.setText(_BREADCRUMBS[indice])

        for i, nombre in enumerate(_NAV_BOTONES):
            getattr(self, nombre).setChecked(indice == i + 1)

        if indice == PAG_DISENO:
            self._cargar_diseno()
        elif indice == PAG_COMPRA:
            self._cargar_compra()
        elif indice == PAG_EDICION:
            self._cargar_edicion()

    def _cargar_diseno(self):
        if self._widget_diseno is None:
            from src.vista.VentanaDiseno import VentanaDiseno
            self._widget_diseno = VentanaDiseno(self.user)
            layout = self.pageDiseno.layout()
            layout.removeWidget(self.lblDisenioPlaceholder)
            self.lblDisenioPlaceholder.hide()
            layout.addWidget(self._widget_diseno)

    def _cargar_compra(self):
        if self._widget_compra is None:
            from src.vista.VentanaCompra import VentanaCompra
            self._widget_compra = VentanaCompra(self.user)
            layout = self.pageCompra.layout()
            layout.removeWidget(self.lblCompraPlaceholder)
            self.lblCompraPlaceholder.hide()
            layout.addWidget(self._widget_compra)

    def _cargar_edicion(self):
        if self._widget_edicion is None:
            from src.vista.VentanaEditar import VentanaEditar
            self._widget_edicion = VentanaEditar(self.user)
            layout = self.pageEdicion.layout()
            layout.removeWidget(self.lblEdicionPlaceholder)
            self.lblEdicionPlaceholder.hide()
            layout.addWidget(self._widget_edicion)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesion",
            "Deseas cerrar la sesion actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
