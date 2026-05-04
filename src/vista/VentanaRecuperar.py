from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.modelo.Logica_login import BussinessObject

Form, Window = uic.loadUiType("./src/vista/ui/vistaRecuperar.ui")

class VentanaRecuperar(QMainWindow, Form):
  def __init__(self):
    super().__init__()
    self.setupUi(self)
    self.logica = BusinessObject()

    self.botonRecuperar.clicked.connect(self.on_actualizar)

  def on_actualizar(self):
    email = self.in_email.text().strip()
    n_contrasena = self.in_nueva_contrasena.text().strip()
    confirmar = self.in_confirmar.text().strip()

    if n_contrasena != confirmar:
      QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
      return

    exito, mensaje = self.logica.actualizarContrasena(email, n_contrasena)
    
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
