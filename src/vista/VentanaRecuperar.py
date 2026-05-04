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
