import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaEditar.ui"
)

# Datos de ejemplo — sustituir por ControladorPaquetes().obtener_todos()
_PAQUETES_EJEMPLO = [
    {
        "id": 1,
        "nombre":    "Escapada Paris",
        "destino":   "Paris, Francia",
        "duracion":  "5",
        "precio":    "1200.00",
        "fecha_ini": "2026-06-01",
        "fecha_fin": "2026-06-06",
        "perfil":    "Parejas",
        "servicios": "Vuelo, Hotel, Traslados",
        "descripcion": "Escapada romantica a la ciudad de la luz con hotel 4 estrellas.",
    },
    {
        "id": 2,
        "nombre":    "Caribe Relax",
        "destino":   "Cancun, Mexico",
        "duracion":  "10",
        "precio":    "2450.00",
        "fecha_ini": "2026-07-15",
        "fecha_fin": "2026-07-25",
        "perfil":    "Familias",
        "servicios": "Vuelo, Hotel All Inclusive, Seguro",
        "descripcion": "Vacaciones en el Caribe con todo incluido para toda la familia.",
    },
    {
        "id": 3,
        "nombre":    "Ruta por Italia",
        "destino":   "Roma, Florencia, Venecia",
        "duracion":  "8",
        "precio":    "980.00",
        "fecha_ini": "2026-05-10",
        "fecha_fin": "2026-05-18",
        "perfil":    "Jovenes",
        "servicios": "Vuelo, Alojamiento, Guia turistico",
        "descripcion": "Recorre las ciudades mas emblematicas de Italia en 8 dias.",
    },
    {
        "id": 4,
        "nombre":    "Safari Kenia",
        "destino":   "Nairobi, Masai Mara",
        "duracion":  "12",
        "precio":    "4800.00",
        "fecha_ini": "2026-08-01",
        "fecha_fin": "2026-08-13",
        "perfil":    "General",
        "servicios": "Vuelo, Lodge, Safari, Seguro",
        "descripcion": "Experiencia unica en la sabana africana con safaris diarios.",
    },
]

_PERFILES = [
    "General", "Familias", "Jovenes", "Jubilados",
    "Parejas", "Grupos escolares", "Movilidad reducida",
]


class VentanaEditar(QWidget):

    def __init__(self, user=None):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.user = user
        self._paquetes = list(_PAQUETES_EJEMPLO)   # copia mutable
        self._paquete_seleccionado = None

        self._conectar_senales()
        self._cargar_lista()
        self._limpiar_formulario()

    # ── Señales ────────────────────────────────────────────────────────────

    def _conectar_senales(self):
        self.listaPaquetes.currentItemChanged.connect(self._on_seleccionar)
        self.inputFiltroLista.textChanged.connect(self._filtrar_lista)
        self.btnGuardarCambios.clicked.connect(self._guardar_cambios)
        self.btnEliminar.clicked.connect(self._eliminar_paquete)
        self.btnLimpiar.clicked.connect(self._limpiar_formulario)

    # ── Lista izquierda ────────────────────────────────────────────────────

    def _cargar_lista(self, filtro=""):
        self.listaPaquetes.clear()
        filtro = filtro.lower()
        for p in self._paquetes:
            if filtro and filtro not in p["nombre"].lower():
                continue
            item = QListWidgetItem(p["nombre"])
            item.setData(Qt.UserRole, p["id"])
            self.listaPaquetes.addItem(item)

    def _filtrar_lista(self, texto):
        self._cargar_lista(filtro=texto)

    def _on_seleccionar(self, item):
        if item is None:
            return
        id_paq = item.data(Qt.UserRole)
        self._paquete_seleccionado = next(
            (p for p in self._paquetes if p["id"] == id_paq), None
        )
        if self._paquete_seleccionado:
            self._rellenar_formulario(self._paquete_seleccionado)

    # ── Formulario ─────────────────────────────────────────────────────────

    def _rellenar_formulario(self, p):
        self.inputNombre.setText(p["nombre"])
        self.inputDestino.setText(p["destino"])
        self.inputDuracion.setText(p["duracion"])
        self.inputPrecio.setText(p["precio"])
        self.inputServicios.setText(p["servicios"])
        self.textDescripcion.setPlainText(p["descripcion"])

        # Perfil
        idx = _PERFILES.index(p["perfil"]) if p["perfil"] in _PERFILES else 0
        self.comboPerfil.setCurrentIndex(idx)

        # Fechas (formato yyyy-MM-dd)
        from PyQt5.QtCore import QDate
        self.inputFechaInicio.setDate(QDate.fromString(p["fecha_ini"], "yyyy-MM-dd"))
        self.inputFechaFin.setDate(QDate.fromString(p["fecha_fin"], "yyyy-MM-dd"))

        self.lblEstado.clear()

    def _limpiar_formulario(self):
        self._paquete_seleccionado = None
        self.listaPaquetes.clearSelection()
        for w in [self.inputNombre, self.inputDestino, self.inputDuracion,
                  self.inputPrecio, self.inputServicios]:
            w.clear()
        self.textDescripcion.clear()
        self.comboPerfil.setCurrentIndex(0)
        self.lblEstado.clear()

    # ── Acciones ───────────────────────────────────────────────────────────

    def _guardar_cambios(self):
        """Req_27: modificar paquete existente."""
        if not self._paquete_seleccionado:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        nombre = self.inputNombre.text().strip()
        destino = self.inputDestino.text().strip()
        if not nombre or not destino:
            self._set_estado("Nombre y Destino son obligatorios.", error=True)
            return

        # Actualizar datos locales (sustituir por ControladorPaquetes().actualizar())
        p = self._paquete_seleccionado
        p["nombre"]      = nombre
        p["destino"]     = destino
        p["duracion"]    = self.inputDuracion.text().strip()
        p["precio"]      = self.inputPrecio.text().strip()
        p["servicios"]   = self.inputServicios.text().strip()
        p["descripcion"] = self.textDescripcion.toPlainText().strip()
        p["perfil"]      = self.comboPerfil.currentText()
        p["fecha_ini"]   = self.inputFechaInicio.date().toString("yyyy-MM-dd")
        p["fecha_fin"]   = self.inputFechaFin.date().toString("yyyy-MM-dd")

        self._cargar_lista(self.inputFiltroLista.text())
        self._set_estado(f"Paquete '{nombre}' actualizado correctamente.")

    def _eliminar_paquete(self):
        """Req_27: eliminar paquete."""
        if not self._paquete_seleccionado:
            self._set_estado("Selecciona un paquete de la lista primero.", error=True)
            return

        nombre = self._paquete_seleccionado["nombre"]
        resp = QMessageBox.question(
            self, "Confirmar eliminacion",
            f"Estas seguro de que quieres eliminar '{nombre}'?\nEsta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        # Eliminar (sustituir por ControladorPaquetes().eliminar(id))
        self._paquetes = [
            p for p in self._paquetes
            if p["id"] != self._paquete_seleccionado["id"]
        ]
        self._limpiar_formulario()
        self._cargar_lista()
        self._set_estado(f"Paquete '{nombre}' eliminado.")

    def _set_estado(self, msg, error=False):
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold;")
