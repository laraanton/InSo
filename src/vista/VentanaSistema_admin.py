"""
VentanaSistema_admin.py  –  Vista de Sistema y Backups
======================================================
Responsabilidad: mostrar información del sistema y delegar
la generación de backups en el Controlador.
No construye rutas de archivo ni hace lógica de negocio.
"""
import platform
from datetime import datetime

from PyQt5.QtWidgets import (
    QPushButton, QMessageBox, QFileDialog, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

from src.vista.VentanaBase import VentanaBase

Form, _ = uic.loadUiType("./src/vista/ui/vistasistemasadmin.ui")


class VentanaSistema_admin(VentanaBase, Form):

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._user    = user
        self._ctrl    = None
        self._backups = []

        self._configurar_info()
        self._configurar_tabla()

    @property
    def controlador(self):
        return self._ctrl

    @controlador.setter
    def controlador(self, value):
        self._ctrl = value
        self.btnBackupAhora.clicked.connect(self._hacer_backup)
        self.cargar()

    # ── Configuración inicial ─────────────────────────────────────────────────

    def _configurar_info(self):
        self.lblPython.setText(f"Python:  {platform.python_version()}")
        self.lblHost.setText("Host BD:  PORTATILMARTA\\SQLEXPRESS")

    def _configurar_tabla(self):
        anchos = [160, 260, 80, 80, 110]
        for i, w in enumerate(anchos):
            self.tablaBackups.setColumnWidth(i, w)
        self.tablaBackups.verticalHeader().setDefaultSectionSize(38)
        self.tablaBackups.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablaBackups.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar(self):
        self._poblar_tabla()

    # ── Backup ────────────────────────────────────────────────────────────────

    def _hacer_backup(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Selecciona carpeta para el backup"
        )
        if not carpeta:
            return

        self.btnBackupAhora.setEnabled(False)
        self.btnBackupAhora.setText("Generando backup…")

        resultado = self._ctrl.hacer_backup(carpeta)

        self.btnBackupAhora.setEnabled(True)
        self.btnBackupAhora.setText("Hacer Backup Ahora")

        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if resultado.ok:
            entrada = {
                "fecha":   ahora,
                "archivo": resultado.mensaje,
                "tamano":  self._tamano_archivo(carpeta, resultado.mensaje),
                "estado":  "OK",
            }
            self._backups.append(entrada)
            self.bkLast1.setText(f"Último backup: {ahora}")
            self._poblar_tabla()
            QMessageBox.information(
                self, "Backup completado",
                f"Copia de seguridad generada correctamente.\nArchivo: {resultado.mensaje}"
            )
        else:
            entrada = {"fecha": ahora, "archivo": "—", "tamano": "—", "estado": "Error"}
            self._backups.append(entrada)
            self._poblar_tabla()
            QMessageBox.critical(self, "Error en backup", resultado.mensaje)

    # ── Tabla de historial ────────────────────────────────────────────────────

    def _poblar_tabla(self):
        tabla = self.tablaBackups
        tabla.setRowCount(0)
        for r in reversed(self._backups):
            row = tabla.rowCount()
            tabla.insertRow(row)
            tabla.setItem(row, 0, self._item(r["fecha"],   center=True))
            tabla.setItem(row, 1, self._item(r["archivo"]))
            tabla.setItem(row, 2, self._item(r["tamano"],  center=True))
            tabla.setItem(row, 3, self._item(r["estado"],  center=True))
            btn = QPushButton("Abrir carpeta")
            btn.setObjectName("btnSecondary")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, arch=r["archivo"]: self._abrir_carpeta(arch))
            tabla.setCellWidget(row, 4, self._wrap(btn))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _tamano_archivo(self, carpeta: str, nombre: str) -> str:
        import os
        try:
            ruta = os.path.join(carpeta, nombre)
            tam  = os.path.getsize(ruta)
            return f"{tam/1_048_576:.1f} MB" if tam > 1_048_576 else f"{tam/1024:.0f} KB"
        except Exception:
            return "—"

    def _abrir_carpeta(self, nombre_archivo: str):
        import subprocess
        try:
            subprocess.Popen(f'explorer /select,"{nombre_archivo}"')
        except Exception:
            pass
