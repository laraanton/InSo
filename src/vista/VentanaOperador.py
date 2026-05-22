import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox

UI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ui",
    "vistaOperador.ui"
)

#indices de cada pantalla, operador -> diseno -> compra -> edicion
PAG_HUB     = 0
PAG_DISENO  = 1
PAG_COMPRA  = 2
PAG_EDICION = 3
PAG_ANALISIS = 4

_TITULOS = [
    "Centro del Operador",
    "Diseno de Paquetes",
    "Gestion de Compra",
    "Edicion de Paquetes",
     "Analisis de Venta",
]
_BREADCRUMBS = [
    "Softrip › Operador",
    "Softrip › Operador › Diseno de Paquetes",
    "Softrip › Operador › Gestion de Compra",
    "Softrip › Operador › Edicion de Paquetes",
    "Softrip › Operador › Analisis de Venta",
]

#etiquetas de los tres botones
_NAV_BOTONES = ["btnNav1", "btnNav2", "btnNav3", "btnNav4"]


class VentanaOperador(QMainWindow): #hereda de la ventana principal

    def __init__(self, user=None):
        super().__init__()
        #cargar ui
        uic.loadUi(UI_FILE, self)

        self.user = user

        nombre = user.nombre_completo if user else "Operador"
        self.userNameLabel.setText(nombre)
        self.avatarLabel.setText(nombre[0].upper() if nombre else "O")

        # Referencias a widgets de sección, se crean solo una vez (lazy)
        #las subventanas solo se crean cuando el usuario entra
        self._widget_diseno  = None
        self._widget_compra  = None
        self._widget_edicion = None
        self._widget_analisis = None 

        #conecta los botones a sus acciones
        self._conectar_senales()
        self._navegar(PAG_HUB)

    def _conectar_senales(self):
        # El logo siempre vuelve al hub principal
        self.logoBtn.clicked.connect(lambda: self._navegar(PAG_HUB))

        #Botones ver más 
        self.moreBtn1.clicked.connect(lambda: self._navegar(PAG_DISENO))
        self.moreBtn2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.moreBtn3.clicked.connect(lambda: self._navegar(PAG_EDICION))
        self.moreBtn4.clicked.connect(lambda: self._navegar(PAG_ANALISIS))

        # Botones de la barra lateral de navegación (misma función, distinto origen)
        self.btnNav1.clicked.connect(lambda: self._navegar(PAG_DISENO))
        self.btnNav2.clicked.connect(lambda: self._navegar(PAG_COMPRA))
        self.btnNav3.clicked.connect(lambda: self._navegar(PAG_EDICION))
        self.btnNav4.clicked.connect(lambda: self._navegar(PAG_ANALISIS))


        # Botón de cerrar sesión
        self.btnLogout.clicked.connect(self._cerrar_sesion)

    def _navegar(self, indice: int):
        # 1. Cambia la página visible del QStackedWidget
        self.stackedWidget.setCurrentIndex(indice)

        # 2. Actualiza el título y el breadcrumb de la cabecera
        self.pageTitle.setText(_TITULOS[indice])
        self.pageBreadcrumb.setText(_BREADCRUMBS[indice])

        # 3. Marca como activo (checked) el botón de navegación correspondiente.
        #    Los botones de nav empiezan en el índice 1 (PAG_DISENO),
        #    por eso se compara indice == i + 1
        for i, nombre in enumerate(_NAV_BOTONES):
            getattr(self, nombre).setChecked(indice == i + 1)

        # 4. Si es la primera vez que se visita esa sección, carga la subventana
        if indice == PAG_DISENO:
            self._cargar_diseno()
        elif indice == PAG_COMPRA:
            self._cargar_compra()
        elif indice == PAG_EDICION:
            self._cargar_edicion()
        elif indice == PAG_ANALISIS:
            self._cargar_analisis()

    def _cargar_diseno(self):
        if self._widget_diseno is None:  #si es la primera vez
            from src.vista.VentanaDiseno import VentanaDiseno
            self._widget_diseno = VentanaDiseno(self.user)

            layout = self.pageDiseno.layout()
            layout.removeWidget(self.lblDisenioPlaceholder) #quita el placeholder(widget vacio en ui para reservar el espacio para la subventana)
            self.lblDisenioPlaceholder.hide()
            layout.addWidget(self._widget_diseno) #inserta el widget real

    def _cargar_compra(self):
        if self._widget_compra is None:
            from src.vista.VentanaCompra import VentanaCompra
            self._widget_compra = VentanaCompra(self.user)

            layout = self.pageCompra.layout()
            layout.removeWidget(self.lblCompraPlaceholder)
            self.lblCompraPlaceholder.hide()
            layout.addWidget(self._widget_compra)

    def _cargar_edicion(self):
        if self._widget_edicion is None:
            from src.vista.VentanaEditar import VentanaEditar
            self._widget_edicion = VentanaEditar(self.user)

            layout = self.pageEdicion.layout()
            layout.removeWidget(self.lblEdicionPlaceholder)
            self.lblEdicionPlaceholder.hide()
            layout.addWidget(self._widget_edicion)

    def _cargar_analisis(self):
        if self._widget_analisis is None:
            from src.vista.VentanaAnalisis import VentanaAnalisis
            self._widget_analisis = VentanaAnalisis(self.user)

            layout = self.pageAnalisis.layout()
            layout.removeWidget(self.lblAnalisisPlaceholder)
            self.lblAnalisisPlaceholder.hide()
            layout.addWidget(self._widget_analisis)

    def _cerrar_sesion(self):
        #muestra un dialogo de confirmación 
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
