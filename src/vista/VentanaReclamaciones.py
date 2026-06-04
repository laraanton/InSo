import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaReclamaciones.ui"
)

_ESTADO_COLORES = {
    "Registrada":   "#1565c0",
    "En revisión":  "#f57c00",
    "En gestión":   "#7b1fa2",
    "Resuelta":     "#2e7d32",
    "Rechazada":    "#c62828",
    "Cerrada":      "#616161",
}


class VentanaReclamaciones(QWidget):

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self._cargar_datos() #arranca cuando el controlador está disponible


    def __init__(self, user=None):
        super().__init__()

        uic.loadUi(UI_FILE, self)

        self.user = user
        self._ctrl = None

        self._reclamaciones = []
        self._id_seleccionado = None

        self._configurar_tabla()
        self._conectar_senales()

    # CONFIGURACIÓN

    def _configurar_tabla(self):
        tabla = self.tablaReclamaciones
        # Stretch: las columnas reparten el espacio disponible en lugar de quedarse con un ancho fijo y dejar espacio vacío.
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.verticalHeader().setVisible(False) # Ocultar los números de fila

    def _conectar_senales(self):

        self.btnBuscar.clicked.connect(self._buscar)
        self.btnLimpiar.clicked.connect(self._limpiar)

        self.inputBuscar.returnPressed.connect(self._buscar)
        
        # Cuando el usuario hace clic en cualquier fila, mostramos su detalle.
        self.tablaReclamaciones.itemSelectionChanged.connect(self._on_seleccion)

        self.btnGuardarEstado.clicked.connect(self._guardar_estado)

    # CARGA Y FILTRADO

    def _cargar_datos(self):
        self._set_estado("Cargando…")

        try:
            self._reclamaciones = self._ctrl.obtener_reclamaciones()
            self._poblar_tabla(self._reclamaciones)
            self._set_estado(f"{len(self._reclamaciones)} reclamaciones encontradas")

        except Exception as e:
            # Si algo falla (BD caída, error de red…) lo mostramos en rojo en lugar de dejar la pantalla congelada sin explicación.
            self._set_estado(f"Error: {e}", error=True)

    def _buscar(self):
        # Leemos los tres filtros de la barra superior.
        texto = self.inputBuscar.text().strip()

        categoria = self.comboCategoria.currentText()
        estado = self.comboEstado.currentText()
        
        # Los valores "Todas las categorías" y "Todos los estados" son el placeholder visual del combo; para el DAO los convertimos a cadena vacía, que significa "sin filtro".
        if categoria == "Todas las categorías":
            categoria = ""

        if estado == "Todos los estados":
            estado = ""

        try:
            resultados = self._ctrl.buscar_reclamaciones(
                texto=texto,
                categoria=categoria,
                estado=estado
            )

            self._poblar_tabla(resultados)

            self._set_estado(f"{len(resultados)} resultado(s)")

        except Exception as e:
            self._set_estado(f"Error: {e}", error=True)

    def _limpiar(self):
        # Vacía el campo de texto y devuelve los combos a su opción inicial (índice 0).

        self.inputBuscar.clear()

        self.comboCategoria.setCurrentIndex(0)
        self.comboEstado.setCurrentIndex(0)
        
        # Recargamos todo desde la BD para asegurarnos de mostrar datos frescos.
        self._cargar_datos()
        # También limpiamos el panel de detalle para que no quede información de la reclamación que estaba seleccionada antes.
        self._limpiar_detalle()

    # TABLA

    def _poblar_tabla(self, reclamaciones):

        tabla = self.tablaReclamaciones

        # Vaciamos las filas existentes antes de pintar las nuevas.
        # Si no lo hiciéramos, los resultados se acumularían.
        tabla.setRowCount(0)

        for r in reclamaciones:

            fila = tabla.rowCount()

            tabla.insertRow(fila)

            #Cols:
            tabla.setItem(fila, 0, self._item(r.pedido_ref))
            tabla.setItem(fila, 1, self._item(r.cliente))
            tabla.setItem(fila, 2, self._item(r.paquete))
            tabla.setItem(fila, 3, self._item(r.tipo))
            tabla.setItem(fila, 4, self._item(r.fecha_pedido))

            estado = r.estado

            item_estado = QTableWidgetItem(estado)

            item_estado.setTextAlignment(Qt.AlignCenter)

            color = _ESTADO_COLORES.get(estado, "#333333")

            item_estado.setForeground(QColor(color))

            tabla.setItem(fila, 5, item_estado)

            tabla.item(fila, 0).setData(Qt.UserRole, r)

        tabla.resizeRowsToContents()

    # DETALLE

    def _on_seleccion(self):
        """Se dispara al hacer clic en una fila — recupera el VO y muestra el detalle."""

        fila = self.tablaReclamaciones.currentRow()
        if fila < 0:
            return

        item = self.tablaReclamaciones.item(fila, 0)
        if not item:
            return

        r = item.data(Qt.UserRole)  # recupera el VO guardado en _poblar_tabla

        if r:
            self._mostrar_detalle(r)

    def _mostrar_detalle(self, r):
        """Rellena el panel derecho con los datos de la reclamación seleccionada."""
        self._id_seleccionado = r.reclamacion_id
        self.lblDetalleTitle.setText(r.pedido_ref or "—")
        self.lblDetalleSub.setText(
            f"{r.paquete}  ·  Pedido {r.pedido_ref}"
        )

        self.lblRef.setText(r.pedido_ref or "—")
        self.lblCliente.setText(r.cliente or "—")
        self.lblCategoria.setText(r.tipo or "—")
        self.lblFecha.setText(r.fecha_pedido or "—")
        self.lblDesc.setText(r.descripcion or "—")
        estado_actual = r.estado

        # Selecciona en el combo el estado actual de esta reclamación
        idx = self.comboEstadoDetalle.findText(estado_actual)

        if idx >= 0:
            self.comboEstadoDetalle.setCurrentIndex(idx)

        # Colorea la categoría con el mismo color que en la tabla
        color = _ESTADO_COLORES.get(estado_actual, "#333333")

        self.lblCategoria.setStyleSheet(
            f"color: {color}; font-weight: bold;"
        )

        self.btnGuardarEstado.setEnabled(True) # habilita el botón ahora que hay selección

    def _limpiar_detalle(self):

        self._id_seleccionado = None

        self.lblDetalleTitle.setText(
            "Selecciona una reclamación"
        )

        self.lblDetalleSub.setText(
            "Haz clic en una fila para ver el detalle"
        )

        self.lblRef.setText("—")
        self.lblCliente.setText("—")
        self.lblCategoria.setText("—")
        self.lblFecha.setText("—")
        self.lblDesc.setText("—")

        self.btnGuardarEstado.setEnabled(False) # deshabilita hasta nueva selección


    # ACTUALIZAR ESTADO

    def _guardar_estado(self):
        """Envía el nuevo estado al controlador y recarga la tabla si tiene éxito."""
        if self._id_seleccionado is None:
            return

        nuevo_estado = self.comboEstadoDetalle.currentText()

        resultado = self._ctrl.cambiar_estado_reclamacion(
            self._id_seleccionado,
            nuevo_estado
        )

        ok = resultado.ok
        msg = resultado.mensaje

        if ok:
            self._set_estado(msg)
            self._cargar_datos() # refresca la tabla con el estado actualizado

        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo actualizar el estado."
            )

    # HELPERS

    @staticmethod
    def _item(texto):
        """Celda de solo lectura — evita que el usuario edite la tabla directamente."""

        it = QTableWidgetItem(str(texto))
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        return it

    def _set_estado(self, msg, error=False):
        # Actualiza la etiqueta de estado en la parte inferior.
        # Verde para info normal, rojo para errores.
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
