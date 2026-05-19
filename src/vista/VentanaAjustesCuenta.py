from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
from src.modelo.dao.UserDAO import UserDAO
from src.modelo.vo.LoginVO import LoginVO
from src.vista.VentanaCliente import VentanaCliente
from src.vista.VentanaMisViajes import VentanaMisViajes

Form, Window = uic.loadUiType("./src/vista/ui/vistaAjustesCuenta.ui")

class VentanaAjustesCuenta(QMainWindow, Form):
    def __init__(self, user):
        super().__init__()
        self.setupUi(self)
        self.user = user
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

    def _connect_signals(self):
        self.logoBtn.clicked.connect(self._volver_principal)
        self.btnNavAjustes.clicked.connect(self._volver_principal)
        self.btnNavViajes.clicked.connect(self._ir_mis_viajes)
        self.btnLogout.clicked.connect(self._cerrar_sesion)
        self.btnEditarPerfil.clicked.connect(self._activar_edicion)
        self.btnGuardarPerfil.clicked.connect(self._guardar_perfil)
        self.btnCambiarPass.clicked.connect(self._cambiar_contrasena)

    def _activar_edicion(self):
        self.in_telefono_edit.setReadOnly(False)
        self.in_preferencia_edit.setEnabled(True)
        self.btnGuardarPerfil.setVisible(True)
        self.btnEditarPerfil.setVisible(False)
        self.in_telefono_edit.setFocus()

    def _guardar_perfil(self):
        telefono = self.in_telefono_edit.text().strip()
        preferencia = self.in_preferencia_edit.currentText()

        dao = UserDAO()
        exito_tel = dao.actualizarTelefono(self.user.usuario_id, telefono)
        exito_pref = dao.actualizarPreferencia(self.user.usuario_id, preferencia)

        if exito_tel and exito_pref:
            self.user = dao.obtenerUsuarioPorId(self.user.usuario_id)
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente")
            # Vuelve a modo lectura
            self.in_telefono_edit.setReadOnly(True)
            self.in_preferencia_edit.setEnabled(False)
            self.btnGuardarPerfil.setVisible(False)
            self.btnEditarPerfil.setVisible(True)
        else:
            QMessageBox.information(self, "Error", "No se pudo actualizar el perfil")

    def _cambiar_contrasena(self):
        pass_actual = self.in_pass_actual.text().strip()
        pass_nueva = self.in_pass_nueva.text().strip()
        pass_confirmar = self.in_pass_confirmar.text().strip()

        if not all([pass_actual, pass_nueva, pass_confirmar]):
            QMessageBox.warning(self, "Error", "Todos los campos de contraseña son obligatorios")
            return
        
        if pass_nueva != pass_confirmar:
            QMessageBox.warning(self, "Error", "Las constraseñas no coinciden")
            return
        
        if len(pass_nueva) < 6:
            QMessageBox.warning(self, "Error", "La nueva contraseña debe tener al menos 6 caracteres")
            return
        
        if pass_actual == pass_nueva:
            QMessageBox.warning(self, "Error", "La nueva contraseña no puede ser igual a la actual")
            return
        
        # Verificar que la contraseña actual es correcta
        loginVO = LoginVO(self.user.email, pass_actual)
        user_check = UserDAO().consultaLogin(LoginVO)
        if not user_check:
            QMessageBox.warning(self, "Error", "La contraseña actual no es correcta")
            return
        
        exito = UserDAO().actualizarContrasena(self.user.usuario_id, pass_nueva)
        if exito:
            QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente")
            self.in_pass_actual.clear()
            self.in_pass_nueva.clear()
            self.in_pass_confirmar.clear()
        else:
            QMessageBox.warning(self, "Error", "No se pudo actualizar la contraseña")

    def _volver_principal(self):
        self.ventana_princial = VentanaCliente(self.user)
        self.ventana_princial.show()
        self.close()

    def _ir_mis_viajes(self):
        self.ventana_princial = VentanaMisViajes(self.user)
        self.ventana_princial.show()
        self.close()
    
    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesion",
            "Deseas cerrar la sesion actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.close()
            from src.vista.Login import MiVentana
            self.login = MiVentana()
            self.login.show()
