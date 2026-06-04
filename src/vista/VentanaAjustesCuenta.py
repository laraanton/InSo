from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
import pyttsx3

Form, Window = uic.loadUiType("./src/vista/ui/vistaAjustesCuenta.ui")


class VentanaAjustesCuenta(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
        self._controlador = None

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self._cargar_datos()
        self._connect_signals()

    def _cargar_datos(self):
        self.userNameLabel.setText(self.user.nombre_completo.split()[0])
        self.avatarLabel.setText(self.user.nombre_completo[0].upper())
        self.in_nombre_completo.setText(self.user.nombre_completo or "")
        self.in_dni.setText(self.user.dni_nie or "")
        self.in_email.setText(self.user.email or "")
        self.in_telefono_edit.setText(self.user.telefono or "")
        self.in_fecha_registro.setText(
            str(self.user.fecha_registro)[:10] if self.user.fecha_registro else "—"
        )
        index = self.in_preferencia_edit.findText(self.user.preferencia or "General")
        if index >= 0:
            self.in_preferencia_edit.setCurrentIndex(index)

        index1 = self.in_preferencia_accesibilidad_edit.findText(
            self.user.preferencia_accesibilidad or "Ninguna"
        )
        if index1 >= 0:
            self.in_preferencia_accesibilidad_edit.setCurrentIndex(index1)

        self.btnLeerPantalla.setVisible(
            getattr(self.user, "preferencia_accesibilidad", "") == "Dificultad lectura"
        )

    def _connect_signals(self):
        self.logoBtn.clicked.connect(self._controlador.volver_a_principal)
        self.btnNavAjustes.clicked.connect(self._controlador.volver_a_principal)
        self.btnNavViajes.clicked.connect(self._controlador.ir_a_mis_viajes)
        self.btnLogout.clicked.connect(self._cerrar_sesion)
        self.btnEditarPerfil.clicked.connect(self._activar_edicion)
        self.btnGuardarPerfil.clicked.connect(self._guardar_perfil)
        self.btnCambiarPass.clicked.connect(self._cambiar_contrasena)
        self.btnLeerPantalla.clicked.connect(self._leer_pantalla)
        self.in_pass_actual.returnPressed.connect(lambda: self.in_pass_nueva.setFocus())
        self.in_pass_nueva.returnPressed.connect(lambda: self.in_pass_confirmar.setFocus())
        self.in_pass_confirmar.returnPressed.connect(self._cambiar_contrasena)

    def _activar_edicion(self):
        self.in_telefono_edit.setReadOnly(False)
        self.in_preferencia_edit.setEnabled(True)
        self.in_preferencia_accesibilidad_edit.setEnabled(True)
        self.btnGuardarPerfil.setVisible(True)
        self.btnEditarPerfil.setVisible(False)
        self.in_telefono_edit.setFocus()

    def _guardar_perfil(self):
        telefono       = self.in_telefono_edit.text().strip()
        preferencia    = self.in_preferencia_edit.currentText()
        preferencia_acc = self.in_preferencia_accesibilidad_edit.currentText()

        ok, msg = self._controlador.guardar_perfil(telefono, preferencia, preferencia_acc)

        if ok:
            QMessageBox.information(self, "Éxito", msg)
            self.in_telefono_edit.setReadOnly(True)
            self.in_preferencia_edit.setEnabled(False)
            self.in_preferencia_accesibilidad_edit.setEnabled(False)
            self.btnGuardarPerfil.setVisible(False)
            self.btnEditarPerfil.setVisible(True)
            # Actualiza el user local con el VO refrescado del controlador
            self.user = self._controlador.user
            self.btnLeerPantalla.setVisible(
                getattr(self.user, "preferencia_accesibilidad", "") == "Dificultad lectura"
            )
        else:
            QMessageBox.warning(self, "Error", msg)

    def _cambiar_contrasena(self):
        pass_actual    = self.in_pass_actual.text().strip()
        pass_nueva     = self.in_pass_nueva.text().strip()
        pass_confirmar = self.in_pass_confirmar.text().strip()

        # La vista solo recoge los campos y llama al controlador
        ok, msg = self._controlador.cambiar_contrasena(
            pass_actual, pass_nueva, pass_confirmar
        )

        if ok:
            QMessageBox.information(self, "Éxito", msg)
            self.in_pass_actual.clear()
            self.in_pass_nueva.clear()
            self.in_pass_confirmar.clear()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión", "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self._controlador.cerrar_sesion()

    def _leer_pantalla(self, *args):
        texto = (
            f"Ajustes de cuenta. "
            f"Nombre completo: {self.user.nombre_completo}. "
            f"DNI: {self.user.dni_nie}. "
            f"Email: {self.user.email}. "
            f"Teléfono: {self.user.telefono or 'No indicado'}. "
            f"Preferencia: {self.user.preferencia or 'General'}. "
            f"Miembro desde: "
            f"{str(self.user.fecha_registro)[:10] if self.user.fecha_registro else 'desconocido'}."
        )
        engine = pyttsx3.init()
        for voice in engine.getProperty("voices"):
            if "spanish" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        engine.say(texto)
        engine.runAndWait()
