from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic

Form, Window = uic.loadUiType("./src/vista/ui/vistaRecuperar.ui")

class VentanaRecuperar(QMainWindow, Form):
    def __init__(self, controlador):
        super().__init__()
        self.setupUi(self)
        self.controlador = controlador

        self.botonRecuperar.clicked.connect(self.on_actualizar)

        self.in_email.returnPressed.connect(lambda: self.in_dni.setFocus())
        self.in_dni.returnPressed.connect(lambda: self.in_nueva_contrasena.setFocus())
        self.in_nueva_contrasena.returnPressed.connect(lambda: self.in_confirmar.setFocus())
        self.in_confirmar.returnPressed.connect(self.on_actualizar)

    def on_actualizar(self):
        email     = self.in_email.text().strip()
        dni       = self.in_dni.text().strip()
        nueva     = self.in_nueva_contrasena.text().strip()
        confirmar = self.in_confirmar.text().strip()

        if not dni:
            QMessageBox.warning(self, "Error", "Debe introducir el DNI para poder actualizar la contraseña.")
            self.in_dni.setFocus()
            return

        if nueva != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        exito, mensaje = self.controlador.actualizarContrasena(email, nueva, dni)
        if not exito:
            QMessageBox.warning(self, "Error", mensaje)
            return

        QMessageBox.information(self, "Éxito", mensaje)
        self.controlador.abrirIniciarSesion()
