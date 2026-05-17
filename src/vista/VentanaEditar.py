"""
VentanaEditar.py  –  Vista de Edición de Paquetes (Req_27)
===========================================================
Responsabilidad: mostrar la lista de paquetes, cargar el formulario al
seleccionar uno y enviar los cambios (o la eliminación) al controlador.

Novedades respecto a la versión anterior:
  · La lista de paquetes muestra el emoji del paquete y un badge
    "· Caducado" en gris si la fecha_fin ya ha pasado.
  · Se añade comboEmoji al formulario para editar el icono del paquete.
  · Un QLabel lblAviso informa visualmente cuando el paquete cargado
    está caducado (fecha_fin < hoy).

Widgets del .ui que usa esta vista:
    listaPaquetes (QListWidget), inputFiltroLista,
    inputNombre, inputDestino, inputDuracion, inputPrecio,
    inputFechaInicio (QDateEdit), inputFechaFin (QDateEdit),
    comboPerfil (QComboBox), comboEmoji (QComboBox),
    inputServicios, textDescripcion,
    lblEstado, lblAviso,
    btnGuardarCambios, btnEliminar, btnLimpiar
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from src.controlador.ControladorOperador import ControladorOperador

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaEditar.ui"
)

_PERFILES = [
    "General", "Familias", "Jovenes", "Jubilados",
    "Parejas", "Grupos escolares", "Movilidad reducida",
]

# Misma lista que en VentanaDiseno para mantener coherencia
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
    ("🎭",  "Máscaras – teatro / cultura"),
]

# ── Helpers de caducidad ───────────────────────────────────────────────────────

def _fecha_fin_caducada(fecha_fin_str: str) -> bool:
    """Devuelve True si la fecha_fin (formato yyyy-MM-dd) es anterior a hoy."""
    if not fecha_fin_str:
        return False
    fecha = QDate.fromString(fecha_fin_str, "yyyy-MM-dd")
    return fecha.isValid() and fecha < QDate.currentDate()


def _texto_lista(paquete: dict) -> str:
    """Compone el texto que se muestra en cada ítem de la lista."""
    emoji = paquete.get("emoji", "")
    nombre = paquete.get("nombre", "Sin nombre")
    prefijo = f"{emoji}  " if emoji else ""
    sufijo = "  · No disponible" if _fecha_fin_caducada(paquete.get("fecha_fin", "")) else ""
    return f"{prefijo}{nombre}{sufijo}"


class VentanaEditar(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = ControladorOperador()
        self._id_seleccionado: int | None = None

        self._inicializar_emojis()
        self._conectar_senales()
        self._recargar_lista()
        self._limpiar_formulario()

    # ── Inicialización ─────────────────────────────────────────────────────

    def _inicializar_emojis(self):
        self.comboEmoji.clear()
        for emoji, descripcion in EMOJIS_PAQUETE:
            self.comboEmoji.addItem(f"{emoji}  {descripcion}", userData=emoji)

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.listaPaquetes.currentItemChanged.connect(self._on_seleccionar)
        self.inputFiltroLista.textChanged.connect(self._recargar_lista)
        self.btnGuardarCambios.clicked.connect(self._guardar_cambios)
        self.btnEliminar.clicked.connect(self._eliminar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    # ── Lista izquierda ────────────────────────────────────────────────────

    def _recargar_lista(self, filtro: str = ""):
        if isinstance(filtro, bool):
            filtro = self.inputFiltroLista.text()
        filtro = filtro.strip().lower()

        self.listaPaquetes.clear()
        for p in self._ctrl.obtener_todos():
            if filtro and filtro not in p["nombre"].lower():
                continue

            item = QListWidgetItem(_texto_lista(p))
            item.setData(Qt.UserRole, p["id"])

            # Ítems caducados → texto atenuado
            if _fecha_fin_caducada(p.get("fecha_fin", "")):
                item.setForeground(QColor("#aaaaaa"))

            self.listaPaquetes.addItem(item)

    def _on_seleccionar(self, item: QListWidgetItem):
        if item is None:
            return
        id_paq = item.data(Qt.UserRole)
        paquete = self._ctrl.obtener_por_id(id_paq)
        if paquete:
            self._id_seleccionado = id_paq
            self._rellenar_formulario(paquete)

    # ── Formulario ─────────────────────────────────────────────────────────

    def _rellenar_formulario(self, p: dict):
        self.inputNombre.setText(p.get("nombre", ""))
        self.inputDestino.setText(p.get("destino", ""))
        self.inputDuracion.setText(p.get("duracion", ""))
        self.inputPrecio.setText(p.get("precio", ""))
        self.inputServicios.setText(p.get("servicios", ""))
        self.textDescripcion.setPlainText(p.get("descripcion", ""))

        # Perfil
        perfil = p.get("perfil", "General")
        idx = _PERFILES.index(perfil) if perfil in _PERFILES else 0
        self.comboPerfil.setCurrentIndex(idx)

        # Emoji: busca por el carácter guardado en userData
        emoji_guardado = p.get("emoji", "")
        idx_emoji = 0
        for i in range(self.comboEmoji.count()):
            if self.comboEmoji.itemData(i) == emoji_guardado:
                idx_emoji = i
                break
        self.comboEmoji.setCurrentIndex(idx_emoji)

        # Fechas
        self.inputFechaInicio.setDate(
            QDate.fromString(p.get("fecha_ini", "2026-01-01"), "yyyy-MM-dd")
        )
        self.inputFechaFin.setDate(
            QDate.fromString(p.get("fecha_fin", "2026-01-01"), "yyyy-MM-dd")
        )

        # Aviso de caducidad
        self._mostrar_aviso_caducidad(p.get("fecha_fin", ""))
        self.lblEstado.clear()

    def _mostrar_aviso_caducidad(self, fecha_fin_str: str):
        """Muestra u oculta el banner de 'No disponible' según la fecha."""
        if _fecha_fin_caducada(fecha_fin_str):
            fecha_fmt = QDate.fromString(fecha_fin_str, "yyyy-MM-dd").toString("dd/MM/yyyy")
            self.lblAviso.setText(f"⚠️  Este paquete no está disponible (fecha de fin: {fecha_fmt})")
            self.lblAviso.setStyleSheet(
                "color: #856404; background-color: #fff3cd; border: 1px solid #ffc107;"
                "border-radius: 6px; padding: 6px 10px; font-size: 11px; font-weight: bold;"
            )
            self.lblAviso.setVisible(True)
        else:
            self.lblAviso.setVisible(False)

    def _limpiar_formulario(self):
        self._id_seleccionado = None
        self.listaPaquetes.clearSelection()
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio, self.inputServicios):
            w.clear()
        self.textDescripcion.clear()
        self.comboPerfil.setCurrentIndex(0)
        self.comboEmoji.setCurrentIndex(0)
        self.lblEstado.clear()
        self.lblAviso.setVisible(False)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_cambios(self):
        if self._id_seleccionado is None:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        datos = {
            "nombre":      self.inputNombre.text().strip(),
            "destino":     self.inputDestino.text().strip(),
            "duracion":    self.inputDuracion.text().strip(),
            "precio":      self.inputPrecio.text().strip(),
            "servicios":   self.inputServicios.text().strip(),
            "descripcion": self.textDescripcion.toPlainText().strip(),
            "perfil":      self.comboPerfil.currentText(),
            "emoji":       self.comboEmoji.currentData(),
            "fecha_ini":   self.inputFechaInicio.date().toString("yyyy-MM-dd"),
            "fecha_fin":   self.inputFechaFin.date().toString("yyyy-MM-dd"),
        }

        ok, msg = self._ctrl.editar_paquete(self._id_seleccionado, datos)
        self._set_estado(msg, error=not ok)
        if ok:
            self._recargar_lista(self.inputFiltroLista.text())
            # Actualizar el aviso si la nueva fecha_fin ya pasó
            self._mostrar_aviso_caducidad(datos["fecha_fin"])

    def _eliminar_paquete(self):
        if self._id_seleccionado is None:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        nombre = self.inputNombre.text() or str(self._id_seleccionado)
        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Seguro que quieres eliminar '{nombre}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        ok, msg = self._ctrl.eliminar_paquete(self._id_seleccionado)
        self._set_estado(msg, error=not ok)
        if ok:
            self._limpiar_formulario()
            self._recargar_lista()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
