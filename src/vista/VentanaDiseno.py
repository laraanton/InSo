"""
VentanaDiseno.py  –  Vista de Diseño de Paquetes (Req_27)
==========================================================
Responsabilidad: recoger los datos del formulario y pasarlos al
ControladorOperador. No contiene lógica de negocio ni acceso a BD.

Widgets del .ui que usa esta vista:
    inputNombre, inputDestino, inputDuracion, inputPrecio,
    inputFechaIni, inputFechaFin,   ← QDateEdit (fecha mínima = hoy)
    comboEmoji,                     ← QComboBox con emoticonos
    textDescripcion, lblEstado,
    btnNuevoPaquete, btnGuardar, btnLimpiar
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDate

from src.controlador.ControladorOperador import ControladorOperador

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaDiseno.ui"
)

# ── Emoticonos disponibles para el paquete ────────────────────────────────────
# Tuplas (emoji, descripción) — se muestran juntos en el combo.
EMOJIS_PAQUETE = [
    ("☀️",  "Sol – destino soleado"),
    ("🌴",  "Palmera – playa tropical"),
    ("🦁",  "León – safari / aventura"),
    ("⛱️",  "Sombrilla – playa y relax"),
    ("❄️",  "Copo de nieve – destino de nieve"),
    ("🏔️",  "Montaña – trekking / naturaleza"),
    ("🚂",  "Tren – viaje ferroviario"),
    ("✈️",  "Avión – viaje internacional"),
    ("🌅",  "Atardecer – viaje romántico"),
    ("🏛️",  "Monumento – turismo cultural"),
    ("🍷",  "Copa de vino – enoturismo / gastronomía"),
    ("🛳️",  "Crucero – viaje en barco"),
    ("🎡",  "Noria – parques y ocio"),
    ("🌿",  "Hoja – ecoturismo / naturaleza"),
    ("🎭",  "Máscaras – turismo cultural y teatro"),
]

# Fechas predeterminadas
_DEFAULT_INI = QDate(2026, 7, 14)
_DEFAULT_FIN = QDate(2026, 7, 31)


class VentanaDiseno(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = ControladorOperador()   # ← único punto de acceso a la lógica
        self._inicializar_emojis()
        self._inicializar_fechas()
        self._conectar_senales()

    # ── Inicialización ─────────────────────────────────────────────────────

    def _inicializar_emojis(self):
        """Rellena el QComboBox con los emoticonos predefinidos."""
        self.comboEmoji.clear()
        for emoji, descripcion in EMOJIS_PAQUETE:
            self.comboEmoji.addItem(f"{emoji}  {descripcion}", userData=emoji)

    def _inicializar_fechas(self):
        """
        Establece la fecha mínima (hoy) y los valores predeterminados
        en ambos QDateEdit. Conecta también la lógica de coherencia
        inicio ≤ fin.
        """
        hoy = QDate.currentDate()

        self.inputFechaIni.setMinimumDate(hoy)
        self.inputFechaFin.setMinimumDate(hoy)

        # Si la fecha predeterminada es anterior a hoy, usar hoy
        self.inputFechaIni.setDate(max(_DEFAULT_INI, hoy))
        self.inputFechaFin.setDate(max(_DEFAULT_FIN, hoy))

        # La fecha de fin no puede ser anterior a la de inicio
        self.inputFechaIni.dateChanged.connect(self._ajustar_fecha_fin)

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.btnNuevoPaquete.clicked.connect(self._limpiar_formulario)
        self.btnGuardar.clicked.connect(self._guardar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_paquete(self):
        """Recoge el formulario y delega en el controlador (Req_27)."""
        emoji_seleccionado = self.comboEmoji.currentData()  # solo el carácter emoji

        datos = {
            "nombre":      self.inputNombre.text().strip(),
            "destino":     self.inputDestino.text().strip(),
            "duracion":    self.inputDuracion.text().strip(),
            "precio":      self.inputPrecio.text().strip(),
            "descripcion": self.textDescripcion.toPlainText().strip(),
            "fecha_ini":   self.inputFechaIni.date().toString("yyyy-MM-dd"),
            "fecha_fin":   self.inputFechaFin.date().toString("yyyy-MM-dd"),
            "emoji":       emoji_seleccionado,
            # Campos pendientes de añadir al .ui:
            "servicios":   "",
            "perfil":      "",
        }

        ok, msg = self._ctrl.crear_paquete(datos)
        self._set_estado(msg, error=not ok)

    def _limpiar_formulario(self):
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio):
            w.clear()
        self.textDescripcion.clear()
        self.lblEstado.clear()

        # Restaurar fechas y emoji predeterminados
        hoy = QDate.currentDate()
        self.inputFechaIni.setDate(max(_DEFAULT_INI, hoy))
        self.inputFechaFin.setDate(max(_DEFAULT_FIN, hoy))
        self.comboEmoji.setCurrentIndex(0)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _ajustar_fecha_fin(self, nueva_ini: QDate):
        """Si la fecha de fin es anterior a la de inicio, la adelanta."""
        if self.inputFechaFin.date() < nueva_ini:
            self.inputFechaFin.setDate(nueva_ini)
        self.inputFechaFin.setMinimumDate(nueva_ini)

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
