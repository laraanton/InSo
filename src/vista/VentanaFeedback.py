import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


# Ruta absoluta al .ui para que no falle si se ejecuta desde otro directorio.
UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaFeedback.ui"
)

# A diferencia de Reclamaciones, aquí el color depende de la puntuación numérica
# (1–5 estrellas), no de un estado textual. Cuanto más baja la nota, más rojo.
_STAR_COLORS = {
    5: "#2e7d32",   # verde oscuro  – excelente
    4: "#5e8d8d",   # teal          – bueno
    3: "#f57c00",   # naranja       – regular
    2: "#e65100",   # naranja oscuro – malo
    1: "#c62828",   # rojo          – muy malo
}


class VentanaFeedback(QWidget):



    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self._cargar_paquetes()  # ← ahora sí, el controlador ya existe
        self._cargar_datos()


    def __init__(self, user=None):
        super().__init__()

        # Carga el diseño visual desde el .ui (hecho con Qt Designer).
        uic.loadUi(UI_FILE, self)

        self.user = user    # usuario logueado (reservado para uso futuro)
        self._ctrl = None      # controlador que centraliza la lógica de negocio
        self._feedbacks: list[dict] = []     # caché local con todos los feedbacks cargados
        self._seleccionado: dict | None = None  # dict del feedback que tiene el foco ahora mismo

        # Orden de arranque: primero el aspecto, luego los combos, luego
        # los eventos, y por último los datos (que dependen de todo lo anterior).
        self._configurar_tabla()
        self._conectar_senales()

    # Configuración inicial 
    def _configurar_tabla(self):
        tabla = self.tablaFeedback

        # Stretch reparte el espacio entre columnas de forma proporcional.
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Los índices de fila (0, 1, 2…) no aportan información útil aquí.
        tabla.verticalHeader().setVisible(False)

        # Ajustes manuales de ancho para las columnas más cortas
        # (referencia, fecha, valoración general, trato operador).
        # Stretch solo aplica a las que no tienen ancho explícito.
        tabla.setColumnWidth(0, 90)   # referencia pedido
        tabla.setColumnWidth(3, 90)   # fecha viaje
        tabla.setColumnWidth(4, 80)   # val. general
        tabla.setColumnWidth(5, 60)   # trato operador

    def _cargar_paquetes(self):
        """Rellena el combo de paquetes con los que tienen feedback."""
        # Solo mostramos paquetes que ya tienen alguna valoración,
        # para no llenar el combo con opciones que no devolverían resultados.
        paquetes = self._ctrl.obtener_paquetes_con_feedback()
        self.comboPaquete.clear()
        self.comboPaquete.addItem("Todos los paquetes")   # opción por defecto = sin filtro
        for p in paquetes:
            self.comboPaquete.addItem(p)

    def _conectar_senales(self):
        # Conectamos cada control de la UI con su función correspondiente.
        self.btnBuscar.clicked.connect(self._buscar)
        self.btnLimpiar.clicked.connect(self._limpiar)

        # Pulsar Enter en el buscador equivale a hacer clic en Buscar.
        self.inputBuscar.returnPressed.connect(self._buscar)

        # Al cambiar la selección en la tabla, actualizamos el panel de detalle.
        self.tablaFeedback.itemSelectionChanged.connect(self._on_seleccion)

    #  Carga y búsqueda 

    def _cargar_datos(self):
        # Avisamos mientras se carga (útil si la BD tarda un momento).
        self._set_estado("Cargando…")
        try:
            self._feedbacks = self._ctrl.obtener_feedbacks()
            self._poblar_tabla(self._feedbacks)
            self._set_estado(f"{len(self._feedbacks)} valoraciones encontradas")
        except Exception as e:
            # Si la BD falla, mostramos el error en rojo en lugar de crashear.
            self._set_estado(f"Error: {e}", error=True)

    def _buscar(self):
        # Recogemos los dos filtros disponibles: texto libre y nombre de paquete.
        texto   = self.inputBuscar.text().strip()
        paquete = self.comboPaquete.currentText()

        # "Todos los paquetes" es el placeholder visual; para el DAO lo
        # convertimos a cadena vacía, que significa "sin filtro".
        if paquete == "Todos los paquetes":
            paquete = ""

        try:
            resultados = self._ctrl.buscar_feedbacks(texto=texto, paquete=paquete)
            self._poblar_tabla(resultados)
            self._set_estado(f"{len(resultados)} resultado(s)")
        except Exception as e:
            self._set_estado(f"Error: {e}", error=True)

    def _limpiar(self):
        # Vaciamos el campo de texto y volvemos el combo a "Todos los paquetes".
        self.inputBuscar.clear()
        self.comboPaquete.setCurrentIndex(0)

        # Recargamos todos los datos desde la BD para tener datos frescos.
        self._cargar_datos()

        # Limpiamos también el panel de detalle para que no quede
        # la información del feedback anterior flotando ahí.
        self._limpiar_detalle()

    #  Tabla 

    def _poblar_tabla(self, feedbacks: list[dict]):
        tabla = self.tablaFeedback

        # Borramos las filas anteriores antes de pintar las nuevas.
        tabla.setRowCount(0)

        for f in feedbacks:
            fila = tabla.rowCount()
            tabla.insertRow(fila)

            # Columnas de texto plano.
            tabla.setItem(fila, 0, self._item(f.pedido_ref))
            tabla.setItem(fila, 1, self._item(f.cliente))
            tabla.setItem(fila, 2, self._item(f.paquete))
            tabla.setItem(fila, 3, self._item(f.fecha_viaje))

            # Valoración general: mostramos estrellas (★★★☆☆) y las coloreamos
            # según la puntuación para leerlo de un vistazo sin mirar el número.
            val = f.val_general
            item_val = QTableWidgetItem(self._estrellas(val))
            item_val.setTextAlignment(Qt.AlignCenter)
            color = _STAR_COLORS.get(val, "#888888")   # gris si el valor es None o inesperado
            item_val.setForeground(QColor(color))
            tabla.setItem(fila, 4, item_val)

            # Trato del operador: misma lógica que la valoración general.
            trato = f.val_trato_operador
            item_trato = QTableWidgetItem(self._estrellas(trato))
            item_trato.setTextAlignment(Qt.AlignCenter)
            item_trato.setForeground(QColor(_STAR_COLORS.get(trato, "#888888")))
            tabla.setItem(fila, 5, item_trato)

            # Guardamos el dict completo en la primera celda para recuperarlo
            # al hacer clic sin necesidad de volver a consultar la BD.
            tabla.item(fila, 0).setData(Qt.UserRole, f)

        # Ajustamos la altura de cada fila al contenido.
        tabla.resizeRowsToContents()

    # Detalle 
    def _on_seleccion(self):
        # Comprobamos que haya algo seleccionado antes de continuar.
        filas = self.tablaFeedback.selectedItems()
        if not filas:
            return

        fila = self.tablaFeedback.currentRow()
        item = self.tablaFeedback.item(fila, 0)
        if not item:
            return

        # Recuperamos el dict guardado con setData(UserRole) en _poblar_tabla.
        f = item.data(Qt.UserRole)
        if f:
            self._mostrar_detalle(f)

    def _mostrar_detalle(self, f: dict):
        # Guardamos el dict por si algún método posterior lo necesita.
        self._seleccionado = f

        # Cabecera del panel: nombre del paquete y datos de contexto.
        self.lblDetalleTitle.setText(f.paquete or "—")
        self.lblDetalleSub.setText(
            f"{f.cliente}  ·  {f.destino}  ·  {f.fecha_viaje}"
        )

        # Función local para formatear una valoración numérica como
        # "★★★☆☆  (3/5)". Si el valor es None mostramos "—".
        def fmt(v):
            return f"{self._estrellas(v)}  ({v}/5)" if v is not None else "—"

        # Rellenamos las cuatro valoraciones del panel.
        self.lblV1.setText(fmt(f.val_trato_operador))
        self.lblV2.setText(fmt(f.val_calidad_transporte))
        self.lblV3.setText(fmt(f.val_satisfaccion_alojamiento))
        self.lblV4.setText(fmt(f.val_general))

        # La valoración general se destaca en color para que sea
        # la primera cifra que capta la atención del operador.
        val = f.val_general
        color = _STAR_COLORS.get(val, "#888888")
        self.lblV4.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")

        # Mostramos el comentario libre del cliente, o un texto neutro si no hay.
        self.lblComentario.setText(f.comentarios or "Sin comentarios.")

    def _limpiar_detalle(self):
        # Devolvemos el panel derecho a su estado inicial vacío.
        self.lblDetalleTitle.setText("Selecciona un feedback")
        self.lblDetalleSub.setText("Haz clic en una fila para ver el detalle")

        # Limpiamos las cuatro etiquetas de valoración y les quitamos
        # cualquier estilo inline que se les hubiera aplicado.
        for lbl in [self.lblV1, self.lblV2, self.lblV3, self.lblV4]:
            lbl.setText("—")
            lbl.setStyleSheet("")   # sin esto, el color de la sesión anterior persiste

        self.lblComentario.setText("—")

    # Helpers 

    @staticmethod
    def _estrellas(val) -> str:
        # Convierte un número (1–5) en una cadena visual de estrellas.
        # Por ejemplo: 3 → "★★★☆☆", None → "—".
        if val is None:
            return "—"
        return "★" * int(val) + "☆" * (5 - int(val))

    @staticmethod
    def _item(texto: str) -> QTableWidgetItem:
        # Crea una celda de solo lectura para que el operador no pueda
        # editar accidentalmente los datos directamente en la tabla.
        it = QTableWidgetItem(str(texto))
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        return it

    def _set_estado(self, msg: str, error: bool = False):
        # Actualiza la etiqueta de estado en la parte inferior de la ventana.
        # Verde para mensajes informativos, rojo para errores.
        self.lblEstado.setText(msg)
        color = "#e05252" if error else "#5e8d8d"
        self.lblEstado.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 11px;"
        )
