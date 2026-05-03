from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from src.vista.Login import MiVentana
from src.modelo.Logica import Logica
from src.controlador.ControladorPrincipal import ControladorPrincipal

import os.path
os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    modelo=Logica()
    controlador= ControladorPrincipal(ventana, modelo)

    ventana.controlador=controlador 
    controlador.ventanaIniciarSesion()

    app.exec_()
