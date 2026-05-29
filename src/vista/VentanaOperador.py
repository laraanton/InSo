"""
VentanaOperador.py  –  Vista principal del módulo Operador
==========================================================
Responsabilidad: construir la UI y conectar cada botón con
el método de navegación correspondiente del ControladorOperador.

NO contiene lógica de negocio, NO instancia subvistas directamente
y NO conoce los índices del QStackedWidget: eso es trabajo del
ControladorOperador.
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from src.controlador.ControladorOperador import ControladorOperador

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaOperador.ui"
)


class VentanaOperador(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)

        self.user = user

        # Datos de cabecera del usuario
        nombre = user.nombre_completo if user else "Operador"
        self.userNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "O")

        # El controlador recibe la ventana para poder manejar la navegación
        self._ctrl = ControladorOperador(
            usuario_id=user.usuario_id if user else None,
            ventana=self,
        )

        self._conectar_senales()
        self._ctrl.navegar_hub()   # página inicial

    # ── Señales 
    # La Vista solo sabe "qué botón se pulsó" y delega en el controlador.
    # No tiene ni índices de página ni lógica de carga de subvistas.

    def _conectar_senales(self):
        # Logo → hub
        self.logoBtn.clicked.connect(self._ctrl.navegar_hub)

        # Cards del hub
        self.moreBtn1.clicked.connect(self._ctrl.navegar_diseno)
        self.moreBtn2.clicked.connect(self._ctrl.navegar_compra)
        self.moreBtn3.clicked.connect(self._ctrl.navegar_edicion)
        self.moreBtn4.clicked.connect(self._ctrl.navegar_analisis)
        self.moreBtn5.clicked.connect(self._ctrl.navegar_feedback)
        self.moreBtn6.clicked.connect(self._ctrl.navegar_reclamaciones)

        # Barra lateral
        self.btnNav1.clicked.connect(self._ctrl.navegar_diseno)
        self.btnNav2.clicked.connect(self._ctrl.navegar_compra)
        self.btnNav3.clicked.connect(self._ctrl.navegar_edicion)
        self.btnNav4.clicked.connect(self._ctrl.navegar_analisis)
        self.btnNav5.clicked.connect(self._ctrl.navegar_feedback)
        self.btnNav6.clicked.connect(self._ctrl.navegar_reclamaciones)

        self.btnLogout.clicked.connect(self._cerrar_sesion)

    # CERRAR SESIÓN

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
