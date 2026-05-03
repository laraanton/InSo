from src.modelo.vo.LoginVO import LoginVO
from src.modelo.Logica import Logica

class ControladorPrincipal:
    def __init__(self, ref_vista, ref_modelo):
      self.__vista = ref_vista
      self._modelo = ref_modelo

    def abrirIniciarSesion(self):
      self.__vista.show()

    def comprobarLogin(self, nombre, passw):
      LoginVO = LoginVO(nombre, passw)
      resultado = self.__modelo.hacerLogin(LoginVO)

      if resultado == None:
        self.__vista.lanzaraviso()

      else:
        self.__vista.close()
