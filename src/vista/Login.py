from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic

Form, Window = uic.loadUiType("./src/vista/ui/vistaLogin.ui")

class MiVentana(QMainWindow, Form):
    def __init__(self, controlador):
        super().__init__()
        self.setupUi(self)
        self.controlador = controlador

        self.forgetPass.setCursor(Qt.PointingHandCursor)
        self.cdRegistro.setCursor(Qt.PointingHandCursor)

        self.botonEntrar.clicked.connect(self.on_button_click)
        self.in_usuario.returnPressed.connect(lambda: self.in_contrasena.setFocus())
        self.in_contrasena.returnPressed.connect(self.on_button_click)
        self.forgetPass.mousePressEvent = lambda event: self.controlador.abrirRecuperar()
        self.cdRegistro.mousePressEvent = lambda event: self.controlador.abrirRegistro()

    def on_button_click(self):
        email     = self.in_usuario.text().strip()
        contrasena = self.in_contrasena.text().strip()

        user, mensaje = self.controlador.comprobarLogin(email, contrasena)
        if not user:
            QMessageBox.warning(self, "Error de acceso", mensaje)
            return

        QMessageBox.information(self, "Bienvenido", mensaje)
        self.controlador.abrirVentanaPrincipal(user)
