import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QSizePolicy
from PyQt5.QtCore import QDate

Form, Window = uic.loadUiType("./src/vista/ui/vistaResultados.ui")


class VentanaResultados(QMainWindow, Form):
    def __init__(self, user, paquetes: list, termino: str, fecha, n_personas):
        super().__init__()
        self.setupUi(self)
        self.user     = user
        self.paquetes = paquetes
        self.termino  = termino
        self.fecha = fecha
        self.personas = n_personas
        self._controlador = None

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, value):
        self._controlador = value
        self._inicializar_buscador()
        self._connect_signals()
        self._poblar_resultados()

    # ── Inicialización ────────────────────────────────────────────────────────

    def _inicializar_buscador(self):
        """Rellena el buscador con el término que ya se buscó y las fechas de hoy."""
        self.in_destino.setText(self.termino)
        hoy = QDate.currentDate()
        self.in_fecha_ida.setDate(hoy)
        self.in_fecha_vuelta.setDate(hoy.addDays(1))
        # Actualiza el avatar del botón cuenta con la inicial del usuario
        self.btnCuenta.setText(self.user.nombre_completo[0].upper())

    def _connect_signals(self):
        self.logoBtn.clicked.connect(self._volver)
        self.btnVolver.clicked.connect(self._volver)
        self.btnBuscar.clicked.connect(self._nueva_busqueda)
        self.btnCuenta.clicked.connect(self._controlador.ir_a_ajustes)

    # ── Resultados ────────────────────────────────────────────────────────────

    def _poblar_resultados(self):
        # Limpia cualquier contenido previo
        while self.listaResultados.count():
            item = self.listaResultados.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        num = len(self.paquetes)
        self.lbl_titulo.setText(
            f"RESULTADOS PARA «{self.termino.upper()}»"
        )
        self.lbl_num_resultados.setText(
            f"{num} paquete{'s' if num != 1 else ''} encontrado{'s' if num != 1 else ''}"
        )

        if not self.paquetes:
            self.scrollResultados.hide()
            self.widgetSinResultados.show()
            return

        self.widgetSinResultados.hide()
        self.scrollResultados.show()

        for p in self.paquetes:
            card = self._crear_tarjeta(p)
            self.listaResultados.addWidget(card)

        self.scrollContentResultados.adjustSize()

    def _crear_tarjeta(self, p: dict) -> QWidget:
        contenedor = QWidget()
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "ui", "cardResultado.ui"),
            contenedor
        )

        duracion = p.get("duracion", "?")
        sufijo   = "noche" if str(duracion) == "1" else "noches"
        contenedor.card_titulo.setText(f"{p.get('destino', '—')} · {duracion} {sufijo}")

        descripcion = p.get("servicios") or (p.get("descripcion", "")[:80])
        contenedor.card_desc.setText(descripcion)

        try:
            precio_txt = f"{float(p.get('precio', 0)):,.2f} € / persona"
        except (ValueError, TypeError):
            precio_txt = f"{p.get('precio', '—')} € / persona"
        contenedor.card_precio.setText(precio_txt)

        perfil = p.get("perfil", "General")
        contenedor.card_chip_perfil.setText(perfil)

        # Chip "Recomendado" solo si coincide con la preferencia del usuario
        pref_usuario = getattr(self.user, "preferencia", "") or ""
        es_recomendado = perfil.lower() == pref_usuario.lower()
        contenedor.card_chip_recomendado.setVisible(es_recomendado)

        # Chip accesible
        contenedor.card_chip_accesible.setVisible(bool(p.get("accesibilidad")))

        pid = p.get("id")
        contenedor.card_btn.clicked.connect(
            lambda _checked, pid=pid: self._ver_paquete(pid)
        )

        contenedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        contenedor.setFixedHeight(120)
        return contenedor

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _nueva_busqueda(self):
        destino      = self.in_destino.text().strip()
        fecha_ida    = self.in_fecha_ida.date()
        fecha_vuelta = self.in_fecha_vuelta.date()

        if not destino:
            self.in_destino.setFocus()
            return
        if fecha_vuelta < fecha_ida:
            return

        nuevos = self._controlador.buscar_paquetes(destino)
        self.paquetes = nuevos
        self.termino  = destino
        self._poblar_resultados()

    def _ver_paquete(self, paquete_id: int):
        self._controlador.ver_paquete_buscado(paquete_id, self.fecha, self.personas)

    def _volver(self):
        self._controlador.volver_a_principal()
