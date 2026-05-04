from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.modelo.Logica_login import BussinessObject

Form, Window = uic.loadUiType("./src/vista/ui/vistaLogin.ui")

class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.logica = BussinessObject()

        self.forgetPass.setCursor(Qt.PointingHandCursor)
        self.cdRegistro.setCursor(Qt.PointingHandCursor)

        self.botonEntrar.clicked.connect(self.on_button_click)
        self.forgetPass.mousePressEvent = lambda event: self.ir_a_recuperar()
        self.cdRegistro.mousePressEvent = lambda event: self.ir_a_registro()

    def on_button_click(self):
        email = self.in_usuario.text().strip()
        contrasena = self.in_contrasena.text().strip()

        user, mensaje = self.logica.comprobarLogin(email, contrasena)
        if not user:
            QMessageBox.warning(self, "Error de acceso", mensaje)
            return

        QMessageBox.information(self, "Bienvenido", mensaje)
        self.abrir_ventana_principal(user)

    def abrir_ventana_principal(self, user):
        # Redirige según el tipo de usuario
        tipo = user.tipo_usuario
        
        #FALTA IMPLEMENTAR
        if tipo == "Administrador":
            from src.vista.VentanaAdmin import VentanaAdmin
            self.ventana = VentanaAdmin(user)
        elif tipo == "Operador":
            from src.vista.VentanaOperador import VentanaOperador
            self.ventana = VentanaOperador(user)
        elif tipo == "Cliente":
            from src.vista.VentanaCliente import VentanaCliente
            self.ventana = VentanaCliente(user)
        else:
            QMessageBox.critical(self, "Error", "Tipo de usuario no reconocido")
            return

        self.ventana.show()
        self.close()

    def ir_a_recuperar(self):
        from src.vista.VentanaRecuperar import VentanaRecuperar
        self.ventana = VentanaRecuperar()
        self.ventana.show()
        self.close()

    def ir_a_registro(self):
        from src.vista.VentanaRegistro import VentanaRegistro
        self.ventana = VentanaRegistro()
        self.ventana.show()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    ventana.show()
    app.exec_()
