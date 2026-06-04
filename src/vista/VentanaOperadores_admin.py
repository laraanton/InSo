"""
VentanaOperadores_admin.py  –  Vista de Gestión de Operadores

    - __init__ recibe user= (no controlador)
    - controlador llega por setter, que llama a cargar()
"""

from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDialogButtonBox,
    QPushButton, QMessageBox, QFileDialog, QHeaderView,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistaoperadoresadmin.ui")


class VentanaOperadores_admin(VentanaBase, Form):

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._user   = user
        self._ctrl   = None
        self._cache  = []

        self._configurar_tabla()

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self._conectar_senales()
        self.cargar()

    # ── Configuración inicial ─────────────────────────────────────────────────

    def _configurar_tabla(self):
        header = self.tablaOperadores.horizontalHeader()

        anchos_fijos = {
            0: 40,
            1: 160,
            2: 100,
            4: 100,
            5: 85,
            6: 95,
        }

        for i in range(self.tablaOperadores.columnCount()):
            if i in anchos_fijos:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.tablaOperadores.setColumnWidth(i, anchos_fijos[i])
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.tablaOperadores.verticalHeader().setDefaultSectionSize(38)
        self.tablaOperadores.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaOperadores.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablaOperadores.horizontalHeader().setStretchLastSection(False)

    def _conectar_senales(self):
        self.btnNuevoOperador.clicked.connect(self._nuevo_operador)
        self.btnExportarOp.clicked.connect(self._exportar)
        self.searchOperadores.textChanged.connect(self._filtrar)
        self.filtroEstadoOp.currentTextChanged.connect(self._filtrar)

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar(self):
        self._cache = self._ctrl.obtener_operadores()
        self._poblar(self._cache)

    def _poblar(self, lista):
        tabla = self.tablaOperadores
        tabla.setRowCount(0)
        for u in lista:
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(str(u.usuario_id), center=True))
            tabla.setItem(row, 1, self._item(u.nombre_completo or ""))
            tabla.setItem(row, 2, self._item(u.dni_nie or ""))
            tabla.setItem(row, 3, self._item(u.email or ""))
            tabla.setItem(row, 4, self._item(u.telefono or "—"))
            fecha = str(u.fecha_registro)[:10] if u.fecha_registro else "—"
            tabla.setItem(row, 6, self._item(fecha, center=True))
            tabla.setCellWidget(row, 5, self._badge_estado(u.estado, u.cuenta_bloqueada))
            tabla.setCellWidget(row, 7, self._acciones(u))

    def _filtrar(self):
        txt    = self.searchOperadores.text().strip().lower()
        estado = self.filtroEstadoOp.currentText()
        filtrados = [
            u for u in self._cache
            if (txt in (u.nombre_completo or "").lower()
                or txt in (u.email or "").lower()
                or txt in (u.dni_nie or "").lower())
            and (estado == "Todos los estados"
                 or (estado == "Bloqueado" and u.cuenta_bloqueada)
                 or (estado != "Bloqueado" and u.estado == estado and not u.cuenta_bloqueada))
        ]
        self._poblar(filtrados)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _nuevo_operador(self):
        dlg = _DialogoOperador(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        d = dlg.datos()
        resultado = self._ctrl.crear_operador(
            d["dni_nie"], d["nombre_completo"], d["email"], d["telefono"], d["password"]
        )
        if resultado.ok:
            QMessageBox.information(self, "Operador creado", resultado.mensaje)
            self.cargar()
        else:
            QMessageBox.warning(self, "Error al crear", resultado.mensaje)

    def _editar_operador(self, usuario):
        dlg = _DialogoOperador(self, usuario)
        if dlg.exec_() != QDialog.Accepted:
            return
        d = dlg.datos()
        resultado = self._ctrl.actualizar_operador(
            usuario, d["telefono"], d["estado"], d["password"] or None
        )
        if resultado.ok:
            QMessageBox.information(self, "Actualizado", resultado.mensaje)
        else:
            QMessageBox.warning(self, "Error", resultado.mensaje)
        self.cargar()

    def _toggle_bloqueo(self, usuario):
        if usuario.cuenta_bloqueada:
            resultado = self._ctrl.desbloquear_operador(usuario)
            titulo = "Cuenta desbloqueada"
        else:
            resultado = self._ctrl.bloquear_operador(usuario)
            titulo = "Cuenta bloqueada"
        if resultado.ok:
            QMessageBox.information(self, titulo, resultado.mensaje)
        else:
            QMessageBox.warning(self, "Error", resultado.mensaje)
        self.cargar()

    def _exportar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar operadores", "operadores.csv", "CSV (*.csv)"
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("ID,Nombre,DNI,Email,Telefono,Estado,Fecha\n")
                for u in self._cache:
                    estado = "Bloqueado" if u.cuenta_bloqueada else u.estado
                    f.write(f"{u.usuario_id},{u.nombre_completo},{u.dni_nie},{u.email},"
                            f"{u.telefono or ''},{estado},{u.fecha_registro or ''}\n")
            QMessageBox.information(self, "Exportado", f"Guardado en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    # ── Widgets de celda ──────────────────────────────────────────────────────

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
        btn_editar = QPushButton("  Editar  ")
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet(
            "QPushButton { background-color:#eef4f4; color:#5e8d8d;"
            " border:1px solid #c5dcdc; border-radius:8px;"
            " font-size:10px; font-weight:bold; padding:2px 0px; }"
            "QPushButton:hover { background-color:#d4e8e8; }"
        )
        btn_editar.clicked.connect(lambda _, u=usuario: self._editar_operador(u))

        if usuario.cuenta_bloqueada:
            etiqueta = "  Desbloquear  "
            estilo = (
                "QPushButton { background-color:#eafaf1; color:#166534;"
                " border:1px solid #b7e4c7; border-radius:8px;"
                " font-size:10px; font-weight:bold; padding:2px 0px; }"
                "QPushButton:hover { background-color:#d4f0e0; }"
            )
        else:
            etiqueta = "  Bloquear  "
            estilo = (
                "QPushButton { background-color:#fee2e2; color:#991b1b;"
                " border:1px solid #f5c6c3; border-radius:8px;"
                " font-size:10px; font-weight:bold; padding:2px 0px; }"
                "QPushButton:hover { background-color:#f9d4d1; }"
            )

        btn_bloquear = QPushButton(etiqueta)
        btn_bloquear.setCursor(Qt.PointingHandCursor)
        btn_bloquear.setStyleSheet(estilo)
        btn_bloquear.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo(u))

        contenedor = QWidget()
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(6)
        lay.addWidget(btn_editar)
        lay.addWidget(btn_bloquear)
        return contenedor


# ── Diálogo de Nuevo / Editar Operador ────────────────────────────────────────

class _DialogoOperador(QDialog):

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self._usuario = usuario
        self.setWindowTitle("Nuevo Operador" if not usuario else "Editar Operador")
        self.setMinimumWidth(440)
        self._build_ui(usuario)

    def _build_ui(self, usuario):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(28, 24, 28, 24)

        titulo = QLabel("Nuevo Operador" if not usuario else "Editar Operador")
        titulo.setObjectName("dlgTitle")
        lay.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.in_dni      = QLineEdit(placeholderText="Ej: 12345678A")
        self.in_nombre   = QLineEdit(placeholderText="Nombre completo")
        self.in_email    = QLineEdit(placeholderText="correo@softrip.es")
        self.in_telefono = QLineEdit(placeholderText="Opcional")
        self.in_password = QLineEdit()
        self.in_password.setEchoMode(QLineEdit.Password)
        self.in_password.setPlaceholderText(
            "Dejar vacío para no cambiar" if usuario else "Mínimo 6 caracteres"
        )
        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Activo", "Inactivo", "Suspendido"])

        if usuario:
            self.in_dni.setText(usuario.dni_nie or "")
            self.in_nombre.setText(usuario.nombre_completo or "")
            self.in_email.setText(usuario.email or "")
            self.in_telefono.setText(usuario.telefono or "")
            idx = self.cb_estado.findText(usuario.estado)
            if idx >= 0:
                self.cb_estado.setCurrentIndex(idx)
            self.in_dni.setEnabled(False)
            self.in_nombre.setEnabled(False)
            self.in_email.setEnabled(False)

        form.addRow("DNI / NIE *",       self.in_dni)
        form.addRow("Nombre completo *",  self.in_nombre)
        form.addRow("Email *",            self.in_email)
        form.addRow("Teléfono",           self.in_telefono)
        form.addRow("Contraseña *",       self.in_password)
        form.addRow("Estado",             self.cb_estado)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Save).setText("Guardar")
        btns.button(QDialogButtonBox.Cancel).setText("Cancelar")
        btns.accepted.connect(self._validar_y_aceptar)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _validar_y_aceptar(self):
        d = self.datos()
        if not self._usuario:
            if not d["dni_nie"]:
                QMessageBox.warning(self, "Campo obligatorio", "El DNI/NIE es obligatorio.")
                return
            if not d["nombre_completo"]:
                QMessageBox.warning(self, "Campo obligatorio", "El nombre completo es obligatorio.")
                return
            if not d["email"]:
                QMessageBox.warning(self, "Campo obligatorio", "El email es obligatorio.")
                return
            if not d["password"]:
                QMessageBox.warning(self, "Campo obligatorio", "La contraseña es obligatoria.")
                return
            if len(d["password"]) < 6:
                QMessageBox.warning(self, "Contraseña corta",
                                    "La contraseña debe tener al menos 6 caracteres.")
                return
        else:
            if d["password"] and len(d["password"]) < 6:
                QMessageBox.warning(self, "Contraseña corta",
                                    "La nueva contraseña debe tener al menos 6 caracteres.")
                return
        self.accept()

    def datos(self):
        return {
            "dni_nie":         self.in_dni.text().strip(),
            "nombre_completo": self.in_nombre.text().strip(),
            "email":           self.in_email.text().strip(),
            "telefono":        self.in_telefono.text().strip(),
            "password":        self.in_password.text().strip(),
            "estado":          self.cb_estado.currentText(),
        }
