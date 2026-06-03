"""
VentanaAdmin.py  –  Vista principal del módulo Administrador
    - __init__ carga la UI (las páginas ya están definidas en vistaAdmin.ui)
    - El controlador llega mediante el setter `controlador`
    - El setter activa _conectar_senales() y llama navegar_dashboard()
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "vistaAdmin.ui")

_MENU_BOTONES = [
    "btnNavDashboard",
    "btnNavOperadores",
    "btnNavUsuarios",
    "btnNavActividad",
    "btnNavSistema",
]


class VentanaAdmin(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user  = user
        self._ctrl = None

        nombre = user.nombre_completo if user else "Administrador"
        self.adminNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "A")

    # ── Setter del controlador ────────────────────────────────────────────────

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self._conectar_senales()
        self._ctrl.navegar_dashboard()

    # ── Señales ───────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.btnNavDashboard.clicked.connect(self._ctrl.navegar_dashboard)
        self.btnNavOperadores.clicked.connect(self._ctrl.navegar_operadores)
        self.btnNavUsuarios.clicked.connect(self._ctrl.navegar_usuarios)
        self.btnNavActividad.clicked.connect(self._ctrl.navegar_actividad)
        self.btnNavSistema.clicked.connect(self._ctrl.navegar_sistema)
        self.btnLogout.clicked.connect(self._cerrar_sesion)

    # ── Cerrar sesión ─────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión", "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self._ctrl.cerrar_sesion()
