from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
from src.controlador.ControladorCliente import ControladorCliente

Form, Window = uic.loadUiType("./src/vista/ui/vistaMisViajes.ui")

class VentanaMisViajes(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self.controlador = ControladorCliente(user)
        self.controlador.ventana_viajes = self
        self._cargar_datos()
        self._connect_signals()

    def _cargar_datos(self):
        self.userNameLabel.setText(self.user.nombre_completo.split()[0])
        self.avatarLabel.setText(self.user.nombre_completo[0].upper())

    def _connect_signals(self):
        self.logoBtn.clicked.connect(self._volver_principal)
        self.btnNavAjustes.clicked.connect(self._ir_ajustes)
        self.btnNavViajes.clicked.connect(self._volver_principal)
        self.btnLogout.clicked.connect(self._cerrar_sesion)

    def _volver_principal(self):
        self.controlador.volver_a_principal()

    def _ir_ajustes(self):
        self.controlador.ir_a_ajustes()


    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.controlador.cerrar_sesion()
