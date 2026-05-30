"""
VentanaBase.py  –  Base común para todas las subvistas del Administrador
========================================================================
Proporciona:
    - Construir celdas de tabla (_item)
    - Envolver widgets en contenedores centrados para celdas (_wrap)
    - Obtener la IP local de la máquina (_ip)
    - Centralizar los colores de badge de estado (ESTADO_COLORES)

NOTA: Sin ningún setStyleSheet aquí. El estilo reside en los .ui / QSS global.
"""

import socket
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem
from PyQt5.QtCore import Qt


class VentanaBase(QWidget):

    ESTADO_COLORES = {
        "Activo":     ("#dcfce7", "#166534"),
        "Bloqueado":  ("#fee2e2", "#991b1b"),
        "Suspendido": ("#fef3c7", "#92400e"),
        "Inactivo":   ("#F3E5F5", "#6A1B9A"),
    }

    def _item(self, texto, center=False, selectable=True):
        item = QTableWidgetItem(str(texto))
        flags = Qt.ItemIsEnabled
        if selectable:
            flags |= Qt.ItemIsSelectable
        item.setFlags(flags)
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def _wrap(self, widget):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(widget)
        return contenedor

    def _ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"
