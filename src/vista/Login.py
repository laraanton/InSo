from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic

Form, Window = uic.loadUiType("./src/vista/ui/vistaLogin.ui")

class MiVentana(QMainWindow, Form):
    def __init__(self):         
        super().__init__()
        self.setupUi(self)
        
        #formato del cursor
        self.forgetPass.setCursor(Qt.PointingHandCursor)
        self.cdRegistro.setCursor(Qt.PointingHandCursor)

        self.in_usuario.returnPressed.connect(lambda: self.in_contrasena.setFocus())
        self.in_contrasena.returnPressed.connect(self.on_button_click)

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self.botonEntrar.clicked.connect(self.on_button_click)
        self.forgetPass.mousePressEvent = lambda event: self._controlador.abrirRecuperar()
        self.cdRegistro.mousePressEvent = lambda event: self._controlador.abrirRegistro()

    def on_button_click(self):
        #limpia las cajas usuario y contrasena
        email     = self.in_usuario.text().strip()
        contrasena = self.in_contrasena.text().strip()

        #llamada al metodo del controlador comprobarLogin
        user, mensaje = self.controlador.comprobarLogin(email, contrasena)
        if not user:
            QMessageBox.warning(self, "Error de acceso", mensaje)
            return

        #si el controlador devuelve user se llama a abrirVentanaPrincipal(admin, operdor o cliente)
        QMessageBox.information(self, "Bienvenido", mensaje)
        self.controlador.abrirVentanaPrincipal(user)
        
    def resetear(self):
        self.in_usuario.clear()
        self.in_contrasena.clear()
        self.in_usuario.setFocus()

