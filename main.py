import os
import sys
from PyQt5.QtWidgets import QApplication
from src.vista.Login import MiVentana
from src.modelo.Logica_login import BussinessObject
from src.controlador.ControladorPrincipal import ControladorPrincipal

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":

    app = QApplication(sys.argv)

    modelo = BussinessObject()
    ventanaLogin = MiVentana()

    controlador = ControladorPrincipal(ventanaLogin, modelo)
    ventanaLogin.controlador = controlador
    controlador.ventanaIniciarSesion()

    sys.exit(app.exec_())
