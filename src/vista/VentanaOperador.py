from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

class SoftripApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("vistaOperador.ui", self)
        self._connect_signals()

    def _connect_signals(self):
        # Navegación
        self.navBtn1.clicked.connect(self.abrir_diseno_paquetes)
        self.navBtn2.clicked.connect(self.abrir_gestion_compra)
        self.navBtn3.clicked.connect(self.abrir_edicion_paquetes)
        # Cards
        self.moreBtn1.clicked.connect(self.abrir_diseno_paquetes)
        self.moreBtn2.clicked.connect(self.abrir_gestion_compra)
        self.moreBtn3.clicked.connect(self.abrir_edicion_paquetes)
        # CTA
        self.ctaButton.clicked.connect(self.prueba_gratis)

    def abrir_diseno_paquetes(self): pass  
    def abrir_gestion_compra(self):  pass  
    def abrir_edicion_paquetes(self): pass  
    def prueba_gratis(self): pass 
