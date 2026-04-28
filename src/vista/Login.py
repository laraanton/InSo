from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.modelo.vo.LoginVo import LoginVo

Form, Window = uic.loadUiType("./src/vista/ui/vistaLogin.ui")

class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Cambiar el color al pasar por arriba
        self.olvidado_contrasena.setStyleSheet("color: blue; text-decoration: underline;")
        self.cdRegistro.setStyleSheet("color: blue; text-decoration: underline;")

        # Cambiar el cursor al pasar por arriba
        self.olvidado_contrasena.setCursor(Qt.PointingHandCursor)
        self.cdRegistro.setCursor(Qt.PointingHandCursor)

        self.botonEntrar.clicked.connect(self.on_button_click)
        self.olvidado_contrasena.mousePressEvent = lambda event: self.ir_a_recuperar()
        self.cdRegistro.mousePressEvent = lambda event: self.ir_a_registro()

    def on_button_click(self):
        texto_usuario = self.in_usuario.text()
        texto_contrasena = self.in_contrasena.text()
        print("Usuario:", texto_usuario)
        print("Contraseña:", texto_contrasena)
        login = LoginVo(texto_usuario, texto_contrasena)
        return login

    def ir_a_recuperar(self):
        print("Ir a recuperar contraseña")
        # from src.vista.VentanaRecuperar import VentanaRecuperar
        # self.ventana = VentanaRecuperar()
        # self.ventana.show()
        # self.close()

    def ir_a_registro(self):
        print("Ir a registro")
        # from src.vista.VentanaRegistro import VentanaRegistro
        # self.ventana = VentanaRegistro()
        # self.ventana.show()
        # self.close()


if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    ventana.show()
    app.exec_()
