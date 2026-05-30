"""
VentanaOperadores_admin.py  –  Vista de Gestión de Operadores
=============================================================
Responsabilidad: mostrar la lista de operadores y delegar
las acciones de creación/edición/bloqueo en el Controlador.
No contiene lógica de negocio ni estilos (el estilo está en el .ui / QSS global).

CORRECCIÓN APLICADA:
  - _DialogoOperador valida internamente antes de llamar accept().
    Antes: btns.accepted → self.accept() (cerraba sin validar).
    Ahora: btns.accepted → _validar_y_aceptar() → self.accept() solo si ok.
    Esto evita que la ventana principal recargue o se cierre con datos incorrectos.
"""

from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDialogButtonBox,
    QPushButton, QMessageBox, QFileDialog, QHeaderView,
    QAbstractItemView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistaoperadoresadmin.ui")


class VentanaOperadores_admin(VentanaBase, Form):

    def __init__(self, controlador, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.controlador = controlador
        self._cache      = []

        self._configurar_tabla()
        self._conectar_senales()

    def _configurar_tabla(self):
        anchos = [50, 180, 110, 170, 110, 90, 100, 160]
        header = self.tablaOperadores.horizontalHeader()
        for i, w in enumerate(anchos):
            if w is None:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.tablaOperadores.setColumnWidth(i, w)
        self.tablaOperadores.verticalHeader().setDefaultSectionSize(38)
        self.tablaOperadores.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaOperadores.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _conectar_senales(self):
        self.btnNuevoOperador.clicked.connect(self._nuevo_operador)
        self.btnExportarOp.clicked.connect(self._exportar)
        self.searchOperadores.textChanged.connect(self._filtrar)
        self.filtroEstadoOp.currentTextChanged.connect(self._filtrar)

    def cargar(self):
        self._cache = self.controlador.obtener_operadores()
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

    def _nuevo_operador(self):
        """
        Abre el diálogo. El diálogo valida internamente antes de aceptar,
        por lo que si llega aquí con Accepted los datos son correctos.

        FIX #1: ControladorAdmin.crear_operador devuelve OperacionResultadoVO,
        NO una tupla (exito, msg). Desempaquetar en tupla lanzaba TypeError
        silenciosa → el QMessageBox nunca aparecía y self.cargar() nunca
        se ejecutaba, por eso la tabla no se actualizaba hasta cerrar sesión.
        """
        dlg = _DialogoOperador(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        d = dlg.datos()
        resultado = self.controlador.crear_operador(          # devuelve OperacionResultadoVO
            d["dni_nie"], d["nombre_completo"], d["email"], d["telefono"], d["password"]
        )
        if resultado.ok:                                       # .ok, no desempaquetar en tupla
            QMessageBox.information(self, "Operador creado", resultado.mensaje)
            self.cargar()
        else:
            QMessageBox.warning(self, "Error al crear", resultado.mensaje)

    def _editar_operador(self, usuario):
        dlg = _DialogoOperador(self, usuario)
        if dlg.exec_() != QDialog.Accepted:
            return
        d = dlg.datos()
        resultado = self.controlador.actualizar_operador(
            usuario, d["telefono"], d["estado"], d["password"] or None
        )
        if resultado.ok:
            QMessageBox.information(self, "Actualizado", resultado.mensaje)
        else:
            QMessageBox.warning(self, "Error", resultado.mensaje)
        self.cargar()

    def _toggle_bloqueo(self, usuario):
        if usuario.cuenta_bloqueada:
            resultado = self.controlador.desbloquear_operador(usuario)
            titulo = "Cuenta desbloqueada"
        else:
            resultado = self.controlador.bloquear_operador(usuario)
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

        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("btnEdit")
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setMinimumWidth(56)
        btn_editar.clicked.connect(lambda _, u=usuario: self._editar_operador(u))

        etiqueta     = "Desbloquear" if usuario.cuenta_bloqueada else "Bloquear"
        btn_bloquear = QPushButton(etiqueta)
        btn_bloquear.setObjectName("btnSuccess" if usuario.cuenta_bloqueada else "btnDanger")
        btn_bloquear.setCursor(Qt.PointingHandCursor)
        btn_bloquear.setMinimumWidth(72)
        btn_bloquear.clicked.connect(lambda _, u=usuario: self._toggle_bloqueo(u))

        lay.addWidget(btn_editar)
        lay.addWidget(btn_bloquear)
        return contenedor


# ── Diálogo de Nuevo / Editar Operador ────────────────────────────────────────

class _DialogoOperador(QDialog):
    """
    Diálogo con validación interna.
    CORRECCIÓN: solo llama self.accept() si todos los campos son válidos,
    evitando que la ventana padre recargue con datos incompletos o erróneos.
    El estilo visual se hereda del QSS global de la aplicación.
    """

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
        # CORRECCIÓN CLAVE: accepted → _validar_y_aceptar, no → self.accept
        btns.accepted.connect(self._validar_y_aceptar)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _validar_y_aceptar(self):
        """Valida todos los campos y solo llama accept() si todo es correcto."""
        d = self.datos()
        if not self._usuario:
            # Nuevo operador: todos los campos obligatorios
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
            # Editar operador: solo validar contraseña si se ha rellenado
            if d["password"] and len(d["password"]) < 6:
                QMessageBox.warning(self, "Contraseña corta",
                                    "La nueva contraseña debe tener al menos 6 caracteres.")
                return
        # Solo aquí el diálogo se cierra con resultado Accepted
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
