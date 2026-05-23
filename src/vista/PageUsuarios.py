import socket
from PyQt5.QtWidgets import (
    QWidget, QTableWidgetItem, QPushButton, QLabel,
    QHBoxLayout, QMessageBox, QFileDialog, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

Form, _ = uic.loadUiType("./src/vista/ui/vistausuariosadmin.ui")


class PageUsuarios(QWidget, Form):

    def __init__(self, dao, usuario_actual, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.dao            = dao
        self.usuario_actual = usuario_actual
        self._cache         = []

        self._configurar_tabla()
        self._conectar_senales()

    def _configurar_tabla(self):
        anchos = [40, 170, 110, 190, 100, 90, 110, 130]
        for i, w in enumerate(anchos):
            self.tablaUsuarios.setColumnWidth(i, w)
        self.tablaUsuarios.verticalHeader().setDefaultSectionSize(38)
        self.tablaUsuarios.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaUsuarios.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _conectar_senales(self):
        self.searchUsuarios.textChanged.connect(self._filtrar)
        self.filtroTipoUs.currentTextChanged.connect(self._filtrar)
        self.filtroEstadoUs.currentTextChanged.connect(self._filtrar)


    def cargar(self):
        self._cache = self.dao.obtenerTodosLosUsuarios()
        self._poblar(self._cache)

    def _poblar(self, lista):
        tabla = self.tablaUsuarios
        tabla.setRowCount(0)
        for u in lista:
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(str(u.usuario_id), center=True))
            tabla.setItem(row, 1, self._item(u.nombre_completo or ""))
            tabla.setItem(row, 2, self._item(u.dni_nie or ""))
            tabla.setItem(row, 3, self._item(u.email or ""))
            tabla.setItem(row, 4, self._item(u.tipo_usuario or ""))
            fecha = str(u.fecha_registro)[:10] if u.fecha_registro else "—"
            tabla.setItem(row, 6, self._item(fecha, center=True))
            tabla.setCellWidget(row, 5, self._badge_estado(u.estado, u.cuenta_bloqueada))
            tabla.setCellWidget(row, 7, self._acciones(u))

    def _filtrar(self):
        txt    = self.searchUsuarios.text().strip().lower()
        tipo   = self.filtroTipoUs.currentText()
        estado = self.filtroEstadoUs.currentText()
        filtrados = [
            u for u in self._cache
            if (txt in (u.nombre_completo or "").lower()
                or txt in (u.email or "").lower()
                or txt in (u.dni_nie or "").lower())
            and (tipo == "Todos los tipos" or u.tipo_usuario == tipo)
            and (estado == "Todos los estados"
                 or (estado == "Bloqueado" and u.cuenta_bloqueada)
                 or (estado != "Bloqueado" and u.estado == estado and not u.cuenta_bloqueada))
        ]
        self._poblar(filtrados)

    def _toggle_bloqueo(self, usuario):
        if usuario.cuenta_bloqueada:
            self.dao.desbloquearCuenta(usuario.usuario_id)
            self.dao.registrarActividad(
                self.usuario_actual.usuario_id, "Bloqueo",
                f"Cuenta desbloqueada: {usuario.email}", self._ip()
            )
        else:
            self.dao.bloquearCuenta(usuario.usuario_id)
            self.dao.registrarActividad(
                self.usuario_actual.usuario_id, "Bloqueo",
                f"Cuenta bloqueada: {usuario.email}", self._ip()
            )
        self.cargar()


    ESTADO_COLORES = {
        "Activo":     ("#dcfce7", "#166534"),
        "Bloqueado":  ("#fee2e2", "#991b1b"),
        "Suspendido": ("#fef3c7", "#92400e"),
        "Inactivo":   ("#F3E5F5", "#6A1B9A"),
    }

    def _badge_estado(self, estado, bloqueada=False):
        if bloqueada:
            texto, (bg, fg) = "Bloqueado", self.ESTADO_COLORES["Bloqueado"]
        else:
            texto = estado or "Desconocido"
            bg, fg = self.ESTADO_COLORES.get(texto, ("#EEEEEE", "#555555"))
        lbl = QLabel(f"  {texto}  ")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background-color:{bg}; color:{fg};"
            "border-radius:8px; font-size:10px; font-weight:bold; padding:2px 0px;"
        )
        return self._wrap(lbl)

    def _acciones(self, usuario):
        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(6)
        etiqueta = "Desbloquear" if usuario.cuenta_bloqueada else "Bloquear"
        btn = QPushButton(etiqueta)
        btn.setObjectName("btnSuccess" if usuario.cuenta_bloqueada else "btnDanger")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo(u))
        lay.addWidget(btn)
        lay.addStretch()
        return contenedor

    def _item(self, texto, center=False):
        item = QTableWidgetItem(str(texto))
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def _wrap(self, widget):
        c = QWidget()
        lay = QHBoxLayout(c)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(widget)
        return c

    def _ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"