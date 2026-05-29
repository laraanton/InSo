from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic

Form, Window = uic.loadUiType("./src/vista/ui/vistaRegistro.ui")

class VentanaRegistro(QMainWindow, Form):
    def __init__(self, controlador):
        super().__init__()
        self.setupUi(self)
        self.controlador = controlador

        self.in_preferencia.wheelEvent  = lambda event: None
        self.in_accesibilidad.wheelEvent = lambda event: None

        self.botonRegistrar.clicked.connect(self.on_registrar)
        self.botonVolver.clicked.connect(self.controlador.abrirIniciarSesion)

        self.in_dni.returnPressed.connect(lambda: self.in_nombre.setFocus())
        self.in_nombre.returnPressed.connect(lambda: self.in_email.setFocus())
        self.in_email.returnPressed.connect(lambda: self.in_telefono.setFocus())
        self.in_telefono.returnPressed.connect(lambda: self.in_contrasena.setFocus())
        self.in_confirmar.returnPressed.connect(self.on_registrar)

    def on_registrar(self):
        dni_nie       = self.in_dni.text().strip()
        nombre        = self.in_nombre.text().strip()
        email         = self.in_email.text().strip()
        telefono      = self.in_telefono.text().strip()
        contrasena    = self.in_contrasena.text().strip()
        confirmar     = self.in_confirmar.text().strip()
        preferencia   = self.in_preferencia.currentText()
        accesibilidad = self.in_accesibilidad.currentText()

        if contrasena != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        exito, mensaje = self.controlador.registrarUsuario(
            dni_nie, nombre, email, telefono, contrasena,
            preferencia, accesibilidad
        )
        if not exito:
            QMessageBox.warning(self, "Error de registro", mensaje)
            return

        QMessageBox.information(self, "Registro exitoso", mensaje)
        self.controlador.abrirIniciarSesion()
