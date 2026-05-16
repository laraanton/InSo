import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaOperador.ui"
)

PAG_HUB     = 0
PAG_DISEÑO  = 1
PAG_COMPRA  = 2
PAG_EDICION = 3

_TITULOS = [
    "Centro del Operador",
    "Diseño de Paquetes",
    "Gestión de Compra",
    "Edición de Paquetes",
]
_BREADCRUMBS = [
    "Softrip › Operador",
    "Softrip › Operador › Diseño de Paquetes",
    "Softrip › Operador › Gestión de Compra",
    "Softrip › Operador › Edición de Paquetes",
]
_NAV_BOTONES = ["btnNav1", "btnNav2", "btnNav3"]


class VentanaOperador(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)

        self.user = user  # UsuarioVO

        # nombre_completo es el atributo real de UsuarioVO
        nombre = user.nombre_completo if user else "Operador"
        self.userNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "O")

        self._conectar_señales()
        self._navegar(PAG_HUB)

    def _conectar_señales(self):
        self.moreBtn1.clicked.connect(lambda: self._navegar(PAG_DISEÑO))
        self.moreBtn2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.moreBtn3.clicked.connect(lambda: self._navegar(PAG_EDICION))

        self.btnNav1.clicked.connect(lambda: self._navegar(PAG_DISEÑO))
        self.btnNav2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.btnNav3.clicked.connect(lambda: self._navegar(PAG_EDICION))

        self.btnLogout.clicked.connect(self._cerrar_sesion)

    def _navegar(self, indice: int):
        self.stackedWidget.setCurrentIndex(indice)
        self.pageTitle.setText(_TITULOS[indice])
        self.pageBreadcrumb.setText(_BREADCRUMBS[indice])

        for i, nombre in enumerate(_NAV_BOTONES):
            getattr(self, nombre).setChecked(indice == i + 1)

        if indice == PAG_DISEÑO:
            self.cargar_diseño()
        elif indice == PAG_COMPRA:
            self.cargar_compra()
        elif indice == PAG_EDICION:
            self.cargar_edicion()

    def cargar_diseño(self):
        self.lblDisenioPlaceholder.setText(
            "📦  Diseño de Paquetes\n\n"
            "Aquí irá el formulario/lista de paquetes turísticos."
        )
        self.lblDisenioPlaceholder.setStyleSheet(
            "font-size: 14px; color: #5e8d8d; font-weight: bold;"
        )

    def cargar_compra(self):
        self.lblCompraPlaceholder.setText(
            "🛒  Gestión de Compra\n\n"
            "Aquí irá la tabla de reservas y estados de pago."
        )
        self.lblCompraPlaceholder.setStyleSheet(
            "font-size: 14px; color: #5e8d8d; font-weight: bold;"
        )

    def cargar_edicion(self):
        self.lblEdicionPlaceholder.setText(
            "✏️  Edición de Paquetes\n\n"
            "Aquí irá el editor de paquetes existentes."
        )
        self.lblEdicionPlaceholder.setStyleSheet(
            "font-size: 14px; color: #5e8d8d; font-weight: bold;"
        )

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
