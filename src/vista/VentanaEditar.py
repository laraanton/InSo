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

EMOJI_PAQUETE = "✈️"

_PERFILES = [
    "General", "Familias", "Jovenes", "Jubilados",
    "Parejas", "Grupos escolares", "Movilidad reducida",
]


def _parse_fecha(s: str) -> QDate:
    s = (s or "").replace("/", "-")
    fecha = QDate.fromString(s, "yyyy-MM-dd")
    return fecha if fecha.isValid() else QDate.currentDate()


def _fecha_fin_caducada(fecha_fin_str: str) -> bool:
    if not fecha_fin_str:
        return False
    fecha = _parse_fecha(fecha_fin_str)
    return fecha.isValid() and fecha < QDate.currentDate()


class VentanaEditar(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._ctrl = ControladorOperador()
        self._id_seleccionado: int | None = None
        self._cargando_formulario: bool = False

        self._conectar_senales()
        self._recargar_lista()
        self._limpiar_formulario()

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.listaPaquetes.currentItemChanged.connect(self._on_seleccionar)
        self.inputFiltroLista.textChanged.connect(self._recargar_lista)
        self.btnEditar.clicked.connect(self._activar_edicion)
        self.btnGuardarCambios.clicked.connect(self._guardar_cambios)
        self.btnEliminar.clicked.connect(self._eliminar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)
        self.inputFechaInicio.dateChanged.connect(lambda _: self._actualizar_fecha_fin())
        self.inputDuracion.textChanged.connect(lambda _: self._actualizar_fecha_fin())

    # ── Lista izquierda ────────────────────────────────────────────────────

    def _recargar_lista(self, filtro: str = ""):
        if isinstance(filtro, bool):
            filtro = self.inputFiltroLista.text()
        filtro = filtro.strip().lower()

        self.listaPaquetes.clear()
        for p in self._ctrl.obtener_todos():
            # p es PaqueteVO — acceso por atributo, no por dict
            nombre = p.nombre or "Sin nombre"
            if filtro and filtro not in nombre.lower():
                continue

            fecha_fin_str = p.fecha_fin or ""
            sufijo = "  · No disponible" if _fecha_fin_caducada(fecha_fin_str) else ""
            item = QListWidgetItem(f"✈️  {nombre}{sufijo}")
            item.setData(Qt.UserRole, p.id)

            if _fecha_fin_caducada(fecha_fin_str):
                item.setForeground(QColor("#aaaaaa"))

            self.listaPaquetes.addItem(item)

    def _on_seleccionar(self, item: QListWidgetItem):
        if item is None:
            return
        id_paq = item.data(Qt.UserRole)
        paquete = self._ctrl.obtener_por_id(id_paq)  # devuelve PaqueteVO
        if paquete:
            self._id_seleccionado = id_paq
            self._rellenar_formulario(paquete)

    # ── Formulario ─────────────────────────────────────────────────────────

    def _rellenar_formulario(self, p):
        """p es PaqueteVO — acceso por atributo."""
        self._cargando_formulario = True

        self.inputNombre.setText(p.nombre or "")
        self.inputDestino.setText(p.destino or "")
        self.inputDuracion.setText(str(p.duracion or ""))
        self.inputPrecio.setText(str(p.precio or ""))
        self.inputServicios.setText(p.servicios or "")
        self.textDescripcion.setPlainText(p.descripcion or "")

        perfil = p.perfil or "General"
        idx = _PERFILES.index(perfil) if perfil in _PERFILES else 0
        self.comboPerfil.setCurrentIndex(idx)

        self.inputFechaInicio.setDate(_parse_fecha(p.fecha_ini or ""))

        self._cargando_formulario = False

        # Calcular fecha_fin = fecha_ini + duración (no usar la de BD)
        self._actualizar_fecha_fin()

        self._mostrar_aviso_caducidad(p.fecha_fin or "")
        self.lblEstado.clear()
        self._set_modo_lectura(True)

    def _mostrar_aviso_caducidad(self, fecha_fin_str: str):
        if _fecha_fin_caducada(fecha_fin_str):
            fecha_fmt = _parse_fecha(fecha_fin_str).toString("dd/MM/yyyy")
            self.lblAviso.setText(
                f"⚠️  Este paquete no está disponible (fecha de fin: {fecha_fmt})"
            )
            self.lblAviso.setStyleSheet(
                "color: #856404; background-color: #fff3cd; border: 1px solid #ffc107;"
                "border-radius: 6px; padding: 6px 10px; font-size: 16px; font-weight: bold;"
            )
            self.lblAviso.setVisible(True)
        else:
            self.lblAviso.setVisible(False)

    def _limpiar_formulario(self):
        self._id_seleccionado = None
        self._cargando_formulario = False
        self.listaPaquetes.clearSelection()
        for w in (self.inputNombre, self.inputDestino,
                  self.inputDuracion, self.inputPrecio, self.inputServicios):
            w.clear()
        self.textDescripcion.clear()
        self.comboPerfil.setCurrentIndex(0)
        self.lblEstado.clear()
        self.lblAviso.setVisible(False)
        hoy = QDate.currentDate()
        self.inputFechaInicio.setDate(hoy)
        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(hoy)
        self.inputFechaFin.setReadOnly(True)
        self._set_modo_lectura(True)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _activar_edicion(self):
        self._set_modo_lectura(False)
        self.btnGuardarCambios.setVisible(True)
        self.btnEditar.setVisible(False)
        self.inputNombre.setFocus()

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
            "emoji":       EMOJI_PAQUETE,
            "fecha_ini":   self.inputFechaInicio.date().toString("yyyy-MM-dd"),
            "fecha_fin":   self.inputFechaFin.date().toString("yyyy-MM-dd"),
        }

        resultado = self._ctrl.editar_paquete(self._id_seleccionado, datos)
        self._set_estado(resultado.mensaje, error=not resultado.ok)
        if resultado.ok:
            self._recargar_lista(self.inputFiltroLista.text())
            self._mostrar_aviso_caducidad(datos["fecha_fin"])
            self._set_modo_lectura(True)

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

        resultado = self._ctrl.eliminar_paquete(self._id_seleccionado)
        self._set_estado(resultado.mensaje, error=not resultado.ok)
        if resultado.ok:
            self._limpiar_formulario()
            self._recargar_lista()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _actualizar_fecha_fin(self):
        if self._cargando_formulario:
            return

        fecha_ini = self.inputFechaInicio.date()
        try:
            dias = int(self.inputDuracion.text().strip())
            if dias < 0:
                dias = 0
        except ValueError:
            dias = 0

        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(fecha_ini.addDays(dias))
        self.inputFechaFin.setReadOnly(True)

    def _set_modo_lectura(self, solo_lectura: bool):
        campos = [
            self.inputNombre, self.inputDestino,
            self.inputDuracion, self.inputPrecio,
            self.inputServicios,
        ]
        for campo in campos:
            campo.setReadOnly(solo_lectura)
        self.textDescripcion.setReadOnly(solo_lectura)
        self.comboPerfil.setEnabled(not solo_lectura)
        self.inputFechaInicio.setReadOnly(solo_lectura)
        self.btnGuardarCambios.setVisible(not solo_lectura)
        self.btnEditar.setVisible(solo_lectura)

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
