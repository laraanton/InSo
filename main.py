import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.controlador.ControladorPrincipal import ControladorPrincipal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = ControladorPrincipal()
    controlador.abrirIniciarSesion()
    sys.exit(app.exec_())
