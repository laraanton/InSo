from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.modelo.Logica_login import BussinessObject

Form, Window = uic.loadUiType("./src/vista/ui/vistaRegistro.ui")

class VentanaRegistro(QMainWindow, Form):
  def __init__(self):
    super().__init__()
    self.setupUi(self)
    self.logica = BusinessObject()

    self.botonRegistrar.clicked.connect(self.on_registrar)

  def on_registrar(self):
    dni_nie = self.in_dni.text().strip()
    nombre = self.in_nombre.text().strip()
    email = self.in_email.text().strip()
    telefono = self.in_telefono.text().strip()
    contrasena = self.in_contrasena.text().strip()
    confirmar = self.in_confirmar.text().strip()

    if contrasena != confirmar:
      QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
      return

    exito, mensaje = self.logica.registrarUsuario(dni_nie, nombre, email, telefono, contrasena)

    if not exito:
      QMessageBox.warning(self, "Error de registro", mensaje)
      return

    QMessageBox.information(self, "Registro exitoso", mensaje)
    self.volver_al_login()

  def volver_al_login(self):
    from src.vista.Login import MiVentana
    self.ventana_login = MiVentana()
    self.ventana_login.show()
    self.close()
    
