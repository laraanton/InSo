"""
LogicaAdmin.py  –  Lógica de negocio del Administrador
=======================================================
Orquesta el AdminDAO y aplica reglas de negocio.
El Controlador NUNCA llama al DAO directamente.

Reglas de negocio aquí:
    - Validación de campos obligatorios al crear operador
    - Validación de longitud mínima de contraseña
    - Construcción de la ruta y nombre del archivo de backup
    - Hash de contraseñas
    - Registro de actividad tras cada mutación
"""

from __future__ import annotations
import hashlib
import os
import socket
from datetime import datetime

from src.modelo.dao.AdminDAO import AdminDAO
from src.modelo.vo.UsuariosVO import UsuarioVO
from src.modelo.vo.RegistroActividadVO import RegistroActividadVO
from src.modelo.vo.OperacionResultadoVO import OperacionResultadoVO


class AdminBO:

    def __init__(self, usuario_actual=None):
        """
        usuario_actual : UsuarioVO del administrador logueado.
        Se usa para registrar su id en el log de actividad.
        """
        self._usuario_actual = usuario_actual
        self._dao = AdminDAO()

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _hashear(password: str) -> str:
        """SHA-256 de la contraseña en texto plano."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def _ip_local() -> str:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

    def _registrar(self, tipo_accion: str, detalle: str):
        """Guarda una entrada en Registro_Actividad usando el usuario actual."""
        if self._usuario_actual is None:
            return
        self._dao.insertar_actividad(
            usuario_id  = self._usuario_actual.usuario_id,
            tipo_accion = tipo_accion,
            detalle     = detalle,
            ip          = self._ip_local(),
        )

    # ── Validaciones ──────────────────────────────────────────────────────────

    @staticmethod
    def _validar_operador(dni_nie: str, nombre_completo: str,
                          email: str, password: str) -> OperacionResultadoVO:
        if not dni_nie.strip():
            return OperacionResultadoVO(False, "El campo 'DNI/NIE' es obligatorio.")
        if not nombre_completo.strip():
            return OperacionResultadoVO(False, "El campo 'Nombre completo' es obligatorio.")
        if not email.strip():
            return OperacionResultadoVO(False, "El campo 'Email' es obligatorio.")
        if not password.strip():
            return OperacionResultadoVO(False, "El campo 'Contraseña' es obligatorio.")
        if len(password.strip()) < 6:
            return OperacionResultadoVO(False, "La contraseña debe tener al menos 6 caracteres.")
        return OperacionResultadoVO(True, "")

    # ── OPERADORES ────────────────────────────────────────────────────────────

    def obtener_operadores(self) -> list[UsuarioVO]:
        return self._dao.obtener_operadores()

    def obtener_todos_usuarios(self) -> list[UsuarioVO]:
        return self._dao.obtener_todos_usuarios()

    def crear_operador(self, dni_nie: str, nombre_completo: str,
                       email: str, telefono: str,
                       password: str) -> OperacionResultadoVO:
        """Valida, hashea la contraseña e inserta el operador."""
        resultado = self._validar_operador(dni_nie, nombre_completo, email, password)
        if not resultado.ok:
            return resultado

        password_hash = self._hashear(password)
        ok = self._dao.insertar_operador(
            dni_nie, nombre_completo, email, telefono, password_hash
        )
        if not ok:
            return OperacionResultadoVO(
                False, "No se pudo crear el operador. El email o DNI ya pueden existir."
            )
        self._registrar("CREAR_OPERADOR",
                        f"Operador creado: {nombre_completo} ({email})")
        return OperacionResultadoVO(True, f"Operador '{nombre_completo}' creado correctamente.")

    def actualizar_operador(self, usuario: UsuarioVO, telefono: str,
                            estado: str, password: str = None) -> OperacionResultadoVO:
        """Actualiza datos del operador. Si se pasa password la valida y hashea."""
        if password:
            if len(password.strip()) < 6:
                return OperacionResultadoVO(
                    False, "La contraseña debe tener al menos 6 caracteres."
                )
            password_hash = self._hashear(password)
        else:
            password_hash = None

        ok = self._dao.actualizar_operador(
            usuario.usuario_id, telefono, estado, password_hash
        )
        if not ok:
            return OperacionResultadoVO(False, "Error al actualizar el operador.")
        self._registrar("EDITAR_OPERADOR",
                        f"Operador actualizado: {usuario.nombre_completo}")
        return OperacionResultadoVO(True, "Datos del operador actualizados correctamente.")

    def bloquear_operador(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        ok = self._dao.bloquear_cuenta(usuario.usuario_id)
        if not ok:
            return OperacionResultadoVO(False, "Error al bloquear la cuenta.")
        self._registrar("BLOQUEAR_CUENTA",
                        f"Cuenta bloqueada: {usuario.nombre_completo}")
        return OperacionResultadoVO(
            True, f"Cuenta de '{usuario.nombre_completo}' bloqueada correctamente."
        )

    def desbloquear_operador(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        ok = self._dao.desbloquear_cuenta(usuario.usuario_id)
        if not ok:
            return OperacionResultadoVO(False, "Error al desbloquear la cuenta.")
        self._registrar("DESBLOQUEAR_CUENTA",
                        f"Cuenta desbloqueada: {usuario.nombre_completo}")
        return OperacionResultadoVO(
            True, f"Cuenta de '{usuario.nombre_completo}' desbloqueada correctamente."
        )

    def bloquear_cuenta(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        """Alias para bloquear cualquier tipo de usuario (no solo operadores)."""
        return self.bloquear_operador(usuario)

    def desbloquear_cuenta(self, usuario: UsuarioVO) -> OperacionResultadoVO:
        """Alias para desbloquear cualquier tipo de usuario."""
        return self.desbloquear_operador(usuario)

    # ── BACKUP ────────────────────────────────────────────────────────────────

    def hacer_backup(self, carpeta: str) -> OperacionResultadoVO:
        """
        Construye el nombre del archivo con timestamp,
        forma la ruta completa y delega la ejecución SQL en el DAO.
        """
        ahora          = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"softrip_backup_{ahora}.bak"
        ruta_completa  = os.path.join(carpeta, nombre_archivo)

        ok = self._dao.hacer_backup(ruta_completa)
        if not ok:
            return OperacionResultadoVO(
                False,
                "No se pudo completar el backup.\n"
                "Asegúrate de que la carpeta es accesible por SQL Server."
            )
        self._registrar("BACKUP", f"Backup generado: {nombre_archivo}")
        return OperacionResultadoVO(True, nombre_archivo)

    # ── REGISTRO DE ACTIVIDAD ─────────────────────────────────────────────────

    def obtener_actividad(self, tipo_accion: str = None,
                          limite: int = 200) -> list[RegistroActividadVO]:
        return self._dao.obtener_actividad(tipo_accion=tipo_accion, limite=limite)
