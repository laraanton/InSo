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


def _texto_lista(paquete: dict) -> str:
    nombre = paquete.get("nombre", "Sin nombre")
    sufijo = "  · No disponible" if _fecha_fin_caducada(paquete.get("fecha_fin", "")) else ""
    return f"✈️  {nombre}{sufijo}"


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
            if filtro and filtro not in p["nombre"].lower():
                continue

            item = QListWidgetItem(_texto_lista(p))
            item.setData(Qt.UserRole, p["id"])

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
            self._cargando_formulario = True

            self.inputNombre.setText(p.get("nombre", ""))
            self.inputDestino.setText(p.get("destino", ""))
            self.inputDuracion.setText(str(p.get("duracion", "")))
            self.inputPrecio.setText(str(p.get("precio", "")))
            self.inputServicios.setText(p.get("servicios", ""))
            self.textDescripcion.setPlainText(p.get("descripcion", ""))

            perfil = p.get("perfil", "General")
            idx = _PERFILES.index(perfil) if perfil in _PERFILES else 0
            self.comboPerfil.setCurrentIndex(idx)

            self.inputFechaInicio.setDate(_parse_fecha(p.get("fecha_ini", "")))

            self._cargando_formulario = False

            # Calcular fecha_fin en base a fecha_ini + duración, no usar la de BD
            self._actualizar_fecha_fin()

            self._mostrar_aviso_caducidad(p.get("fecha_fin", ""))
            self.lblEstado.clear()

    def _mostrar_aviso_caducidad(self, fecha_fin_str: str):
        if _fecha_fin_caducada(fecha_fin_str):
            fecha_fmt = _parse_fecha(fecha_fin_str).toString("dd/MM/yyyy")
            self.lblAviso.setText(f"⚠️  Este paquete no está disponible (fecha de fin: {fecha_fmt})")
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
        # ── resetear fechas ──────────────────────────────────────────────────
        hoy = QDate.currentDate()
        self.inputFechaInicio.setDate(hoy)
        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(hoy)
        self.inputFechaFin.setReadOnly(True)

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_cambios(self):
        if self._id_seleccionado is None:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        datos = {
            "nombre": self.inputNombre.text().strip(),
            "destino": self.inputDestino.text().strip(),
            "duracion": self.inputDuracion.text().strip(),
            "precio": self.inputPrecio.text().strip(),
            "servicios": self.inputServicios.text().strip(),
            "descripcion": self.textDescripcion.toPlainText().strip(),
            "perfil": self.comboPerfil.currentText(),
            "emoji": EMOJI_PAQUETE,
            "fecha_ini": self.inputFechaInicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.inputFechaFin.date().toString("yyyy-MM-dd"),
        }

        ok, msg = self._ctrl.editar_paquete(self._id_seleccionado, datos)
        self._set_estado(msg, error=not ok)
        if ok:
            self._recargar_lista(self.inputFiltroLista.text())
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

    def _actualizar_fecha_fin(self):
        print(f">>> actualizar_fecha_fin | cargando={self._cargando_formulario} | duracion='{self.inputDuracion.text()}'")
        if self._cargando_formulario:
            return

        fecha_ini = self.inputFechaInicio.date()
        try:
            dias = int(self.inputDuracion.text().strip())
            if dias < 0:
                dias = 0
        except ValueError:
            dias = 0

        print(f">>> setDate → {fecha_ini.addDays(dias).toString('dd/MM/yyyy')}")
        self.inputFechaFin.setReadOnly(False)
        self.inputFechaFin.setDate(fecha_ini.addDays(dias))
        self.inputFechaFin.setReadOnly(True)

    def _set_estado(self, msg: str, error: bool = False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
