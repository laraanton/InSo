from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic

Form, Window = uic.loadUiType("./src/vista/ui/vistaMisViajes.ui")

class VentanaMisViajes(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
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
        from src.vista.VentanaCliente import VentanaCliente
        self.ventana_principal = VentanaCliente(self.user)
        self.ventana_principal.show()
        self.hide()

    def _ir_ajustes(self):
        from src.vista.VentanaAjustesCuenta import VentanaAjustesCuenta
        self.ventana_ajustes = VentanaAjustesCuenta(self.user)
        self.ventana_ajustes.show()
        self.hide()

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
            self.close()
