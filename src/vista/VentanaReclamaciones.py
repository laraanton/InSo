"""
VentanaReclamaciones.py  –  Vista de Reclamaciones (Operador)
=============================================================
El operador puede consultar, filtrar y cambiar el estado
de las reclamaciones.
Se inyecta como página dentro del QStackedWidget de VentanaOperador.
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.controlador.ControladorOperador import ControladorOperador

# Ruta absoluta al .ui para que funcione sin importar desde dónde
# se ejecute el programa (evita el clásico "fichero no encontrado").
UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaReclamaciones.ui"
)

# Cada estado tiene un color asociado para que visualmente
# se distinga de un vistazo si algo está resuelto, pendiente, etc.
_ESTADO_COLORES = {
    "Registrada":   "#1565c0",  # azul   – recién creada, nadie la ha tocado
    "En revisión":  "#f57c00",  # naranja – alguien la está mirando
    "En gestión":   "#7b1fa2",  # morado  – ya se está actuando sobre ella
    "Resuelta":     "#2e7d32",  # verde   – solucionada
    "Rechazada":    "#c62828",  # rojo    – no se va a atender
    "Cerrada":      "#616161",  # gris    – archivada, ya no activa
}


class VentanaReclamaciones(QWidget):

    def __init__(self, user=None):
        super().__init__()

        # Carga el diseño visual desde el archivo .ui (creado con Qt Designer).
        # Todo lo que hay en ese XML se convierte en widgets accesibles por nombre.
        uic.loadUi(UI_FILE, self)

        self.user = user                        # usuario logueado (por si hace falta en el futuro)
        self._ctrl = ControladorOperador()      # controlador que centraliza la lógica de negocio
        self._reclamaciones: list[dict] = []   # caché local de las reclamaciones cargadas
        self._id_seleccionado: int | None = None  # ID de la fila que el operador tiene seleccionada

        # Tres pasos de arranque en orden lógico:
        self._configurar_tabla()    # 1. aspecto visual de la tabla
        self._conectar_senales()    # 2. qué hace cada botón
        self._cargar_datos()        # 3. traer los datos de la BD y pintarlos

    # Configuración inicial 

    def _configurar_tabla(self):
        tabla = self.tablaReclamaciones

        # Stretch hace que las columnas repartan el espacio disponible
        # en lugar de quedarse con un ancho fijo y dejar espacio vacío.
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Los números de fila (0, 1, 2…) no aportan nada aquí, los ocultamos.
        tabla.verticalHeader().setVisible(False)

    def _conectar_senales(self):
        # Cada línea conecta un evento de la interfaz con el método que lo maneja.
        # Esto separa "qué dispara la acción" de "qué hace la acción".

        self.btnBuscar.clicked.connect(self._buscar)
        self.btnLimpiar.clicked.connect(self._limpiar)

        # Pulsar Enter en el campo de texto es igual que hacer clic en Buscar.
        self.inputBuscar.returnPressed.connect(self._buscar)

        # Cuando el usuario hace clic en cualquier fila, mostramos su detalle.
        self.tablaReclamaciones.itemSelectionChanged.connect(self._on_seleccion)

        self.btnGuardarEstado.clicked.connect(self._guardar_estado)

    # ── Carga y búsqueda 

    def _cargar_datos(self):
        # Avisamos mientras se carga (en BD lentas o remotas esto se nota).
        self._set_estado("Cargando…")
        try:
            self._reclamaciones = self._ctrl.obtener_reclamaciones()
            self._poblar_tabla(self._reclamaciones)
            self._set_estado(f"{len(self._reclamaciones)} reclamaciones encontradas")
        except Exception as e:
            # Si algo falla (BD caída, error de red…) lo mostramos en rojo
            # en lugar de dejar la pantalla congelada sin explicación.
            self._set_estado(f"Error: {e}", error=True)

    def _buscar(self):
        # Leemos los tres filtros de la barra superior.
        texto     = self.inputBuscar.text().strip()
        categoria = self.comboCategoria.currentText()
        estado    = self.comboEstado.currentText()

        # Los valores "Todas las categorías" y "Todos los estados" son
        # el placeholder visual del combo; para el DAO los convertimos a
        # cadena vacía, que significa "sin filtro".
        if categoria == "Todas las categorías":
            categoria = ""
        if estado == "Todos los estados":
            estado = ""

        try:
            resultados = self._ctrl.buscar_reclamaciones(texto=texto, categoria=categoria, estado=estado)
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

        # También limpiamos el panel de detalle para que no quede
        # información de la reclamación que estaba seleccionada antes.
        self._limpiar_detalle()

    # Creacion de la TABLA

    def _poblar_tabla(self, reclamaciones: list[dict]):
        tabla = self.tablaReclamaciones

        # Vaciamos las filas existentes antes de pintar las nuevas.
        # Si no lo hiciéramos, los resultados se acumularían.
        tabla.setRowCount(0)

        for r in reclamaciones:
            fila = tabla.rowCount()
            tabla.insertRow(fila)

            # Columnas básicas: referencia, cliente, paquete, categoría, fecha.
            tabla.setItem(fila, 0, self._item(r.get("ref_reclamacion", "")))
            tabla.setItem(fila, 1, self._item(r.get("cliente", "")))
            tabla.setItem(fila, 2, self._item(r.get("paquete", "")))
            tabla.setItem(fila, 3, self._item(r.get("categoria", "")))
            tabla.setItem(fila, 4, self._item(r.get("fecha_incidente", "")))

            # La columna de estado se pinta de color según el diccionario de arriba.
            estado = r.get("estado_reclamacion", "")
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignCenter)
            color = _ESTADO_COLORES.get(estado, "#333333")  # gris oscuro si el estado es desconocido
            item_estado.setForeground(QColor(color))
            tabla.setItem(fila, 5, item_estado)

            # Truco importante: guardamos el dict completo en la primera celda.
            # Así, cuando el usuario haga clic en la fila, podemos recuperar
            # todos los datos sin tener que volver a consultar la BD.
            tabla.item(fila, 0).setData(Qt.UserRole, r)

        # Ajustamos la altura de cada fila al contenido (por si el texto ocupa más de una línea).
        tabla.resizeRowsToContents()

    # ── Mostrar en detalle el seleccionado

    def _on_seleccion(self):
        fila = self.tablaReclamaciones.currentRow()
        if fila < 0:
            return  # no hay nada seleccionado (puede pasar al limpiar la tabla)

        item = self.tablaReclamaciones.item(fila, 0)
        if not item:
            return  # celda vacía, no hacemos nada

        # Recuperamos el dict que guardamos antes con setData(UserRole).
        r = item.data(Qt.UserRole)
        if r:
            self._mostrar_detalle(r)

    def _mostrar_detalle(self, r: dict):
        # Guardamos el ID para saber a qué reclamación actualizar cuando
        # el operador pulse "Guardar estado".
        self._id_seleccionado = r.get("reclamacion_id")

        # Cabecera del panel de detalle.
        self.lblDetalleTitle.setText(r.get("ref_reclamacion", "—"))
        self.lblDetalleSub.setText(
            f"{r.get('paquete', '—')}  ·  Pedido {r.get('ref_pedido', '—')}"
        )

        # Campos de información de solo lectura.
        self.lblRef.setText(r.get("ref_reclamacion", "—"))
        self.lblCliente.setText(r.get("cliente", "—"))
        self.lblCategoria.setText(r.get("categoria", "—"))
        self.lblFecha.setText(r.get("fecha_incidente", "—"))
        self.lblDesc.setText(r.get("descripcion_incidente", "—"))

        # Sincronizamos el combo del detalle con el estado actual de la reclamación.
        # findText devuelve el índice, o -1 si no lo encuentra.
        estado_actual = r.get("estado_reclamacion", "Registrada")
        idx = self.comboEstadoDetalle.findText(estado_actual)
        if idx >= 0:
            self.comboEstadoDetalle.setCurrentIndex(idx)

        # Coloreamos la categoría con el color del estado para dar contexto visual
        # de "qué tan urgente" es sin tener que leer el combo.
        color = _ESTADO_COLORES.get(estado_actual, "#333333")
        self.lblCategoria.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Habilitamos el botón solo cuando hay algo seleccionado.
        self.btnGuardarEstado.setEnabled(True)

    def _limpiar_detalle(self):
        # Restablecemos el panel derecho a su estado "vacío" inicial.
        self._id_seleccionado = None
        self.lblDetalleTitle.setText("Selecciona una reclamación")
        self.lblDetalleSub.setText("Haz clic en una fila para ver el detalle")
        self.lblRef.setText("—")
        self.lblCliente.setText("—")
        self.lblCategoria.setText("—")
        self.lblFecha.setText("—")
        self.lblDesc.setText("—")

        # Sin selección no tiene sentido dejar el botón activo.
        self.btnGuardarEstado.setEnabled(False)

    # ── Guardar estado 

    def _guardar_estado(self):
        if self._id_seleccionado is None:
            return  # salvaguarda: no debería llegar aquí con el botón deshabilitado

        nuevo_estado = self.comboEstadoDetalle.currentText()

        # El controlador devuelve (True, msg) si la actualización fue bien, (False, msg) si no.
        ok, msg = self._ctrl.cambiar_estado_reclamacion(self._id_seleccionado, nuevo_estado)

        if ok:
            self._set_estado(msg)
            # Recargamos la tabla para que el cambio se refleje de inmediato.
            self._cargar_datos()
        else:
            QMessageBox.warning(
                self, "Error", "No se pudo actualizar el estado. Inténtalo de nuevo."
            )

    # ── Helpers 

    @staticmethod
    def _item(texto: str) -> QTableWidgetItem:
        # Crea una celda de solo lectura. Sin esto el usuario podría
        # editar el contenido de la tabla directamente, lo que no queremos.
        it = QTableWidgetItem(str(texto))
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        return it

    def _set_estado(self, msg: str, error: bool = False):
        # Actualiza la etiqueta de estado en la parte inferior.
        # Verde para info normal, rojo para errores.
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 11px;"
        )
