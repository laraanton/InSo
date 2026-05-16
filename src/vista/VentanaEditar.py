"""
VentanaEditar.py  –  Vista de Edición de Paquetes (Req_27)
===========================================================
Responsabilidad: mostrar la lista de paquetes, cargar el formulario al
seleccionar uno y enviar los cambios (o la eliminación) al controlador.

Widgets del .ui que usa esta vista:
    listaPaquetes (QListWidget), inputFiltroLista,
    inputNombre, inputDestino, inputDuracion, inputPrecio,
    inputFechaInicio (QDateEdit), inputFechaFin (QDateEdit),
    comboPerfil (QComboBox), inputServicios,
    textDescripcion, lblEstado,
    btnGuardarCambios, btnEliminar, btnLimpiar
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QDate

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


class VentanaEditar(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = ControladorOperador()
        self._id_seleccionado: int | None = None

        self._conectar_senales()
        self._recargar_lista()
        self._limpiar_formulario()

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.listaPaquetes.currentItemChanged.connect(self._on_seleccionar)
        self.inputFiltroLista.textChanged.connect(self._recargar_lista)
        self.btnGuardarCambios.clicked.connect(self._guardar_cambios)
        self.btnEliminar.clicked.connect(self._eliminar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    # ── Lista izquierda ────────────────────────────────────────────────────

    def _recargar_lista(self, filtro: str = ""):
        """Pide la lista al controlador y la muestra en listaPaquetes."""
        if isinstance(filtro, bool):   # señal textChanged pasa el texto, no bool
            filtro = self.inputFiltroLista.text()
        filtro = filtro.strip().lower()

        self.listaPaquetes.clear()
        for p in self._ctrl.obtener_todos():
            if filtro and filtro not in p["nombre"].lower():
                continue
            item = QListWidgetItem(p["nombre"])
            item.setData(Qt.UserRole, p["id"])
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

        perfil = p.get("perfil", "General")
        idx = _PERFILES.index(perfil) if perfil in _PERFILES else 0
        self.comboPerfil.setCurrentIndex(idx)

        self.inputFechaInicio.setDate(
            QDate.fromString(p.get("fecha_ini", "2026-01-01"), "yyyy-MM-dd")
        )
        self.inputFechaFin.setDate(
            QDate.fromString(p.get("fecha_fin", "2026-01-01"), "yyyy-MM-dd")
        )
        self.lblEstado.clear()

    def _limpiar_formulario(self):
        self._id_seleccionado = None
        self.listaPaquetes.clearSelection()
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio, self.inputServicios):
            w.clear()
        self.textDescripcion.clear()
        self.comboPerfil.setCurrentIndex(0)
        self.lblEstado.clear()

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_cambios(self):
        """Recoge el formulario y llama al controlador para editar (Req_27)."""
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
            "fecha_ini":   self.inputFechaInicio.date().toString("yyyy-MM-dd"),
            "fecha_fin":   self.inputFechaFin.date().toString("yyyy-MM-dd"),
        }

        ok, msg = self._ctrl.editar_paquete(self._id_seleccionado, datos)
        self._set_estado(msg, error=not ok)
        if ok:
            self._recargar_lista(self.inputFiltroLista.text())

    def _eliminar_paquete(self):
        """Pide confirmación y llama al controlador para eliminar (Req_27)."""
        if self._id_seleccionado is None:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        nombre = self.inputNombre.text() or str(self._id_seleccionado)
        resp = QMessageBox.question(
            self, "Confirmar eliminacion",
            f"¿Seguro que quieres eliminar '{nombre}'?\nEsta accion no se puede deshacer.",
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
