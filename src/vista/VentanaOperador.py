import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "vistaOperador.ui")


class VentanaOperador(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = None

        nombre = user.nombre_completo if user else "Operador"
        self.userNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "O")

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self._conectar_senales()
        self._ctrl.navegar_hub()

    def _conectar_senales(self):
        self.logoBtn.clicked.connect(self._ctrl.navegar_hub)
        self.moreBtn1.clicked.connect(self._ctrl.navegar_diseno)
        self.moreBtn2.clicked.connect(self._ctrl.navegar_compra)
        self.moreBtn3.clicked.connect(self._ctrl.navegar_edicion)
        self.moreBtn4.clicked.connect(self._ctrl.navegar_analisis)
        self.moreBtn5.clicked.connect(self._ctrl.navegar_feedback)
        self.moreBtn6.clicked.connect(self._ctrl.navegar_reclamaciones)
        self.btnNav1.clicked.connect(self._ctrl.navegar_diseno)
        self.btnNav2.clicked.connect(self._ctrl.navegar_compra)
        self.btnNav3.clicked.connect(self._ctrl.navegar_edicion)
        self.btnNav4.clicked.connect(self._ctrl.navegar_analisis)
        self.btnNav5.clicked.connect(self._ctrl.navegar_feedback)
        self.btnNav6.clicked.connect(self._ctrl.navegar_reclamaciones)
        self.btnLogout.clicked.connect(self._cerrar_sesion)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión", "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self._ctrl.cerrar_sesion()
