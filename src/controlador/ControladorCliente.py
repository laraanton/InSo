from src.modelo.Logica_login import BussinessObject
from src.modelo.dao.UserDAO import UserDAO
from src.modelo.dao.CuentaDAO import CuentaDAO
from src.modelo.dao.PedidoDAO import PedidoDAO
from src.modelo.vo.LoginVO import LoginVO
from src.modelo.vo.PedidoVO import PedidoVO


class ControladorCliente:
    def __init__(self, user):
        self.user = user
        self.logica = BussinessObject()
        self.ventana_principal = None
        self.ventana_ajustes = None
        self.ventana_viajes = None
        self.ventana_detalle = None
        self.ventana_compra = None

    # ── Navegación ───────────────────────────────────────────────────────────

    def abrir_principal(self):
        from src.vista.VentanaCliente import VentanaCliente
        self.ventana_principal = VentanaCliente(self.user)
        self.ventana_principal.show()

    def ir_a_ajustes(self):
        from src.vista.VentanaAjustesCuenta import VentanaAjustesCuenta
        self.ventana_ajustes = VentanaAjustesCuenta(self.user)
        self.ventana_ajustes.show()
        self._ocultar_todas_menos(self.ventana_ajustes)

    def ir_a_mis_viajes(self):
        from src.vista.VentanaMisViajes import VentanaMisViajes
        self.ventana_viajes = VentanaMisViajes(self.user)
        self.ventana_viajes.show()
        self._ocultar_todas_menos(self.ventana_viajes)

    def volver_a_principal(self):
        self._ocultar_todas_menos(None)
        self.abrir_principal()

    def cerrar_sesion(self):
        from src.vista.Login import MiVentana
        self._cerrar_todo()
        self.ventana_login = MiVentana()
        self.ventana_login.show()

    def _ocultar_todas_menos(self, excepcion):
        for v in [self.ventana_principal, self.ventana_ajustes,
                  self.ventana_viajes, self.ventana_detalle, self.ventana_compra]:
            if v and v is not excepcion:
                v.hide()

    def _cerrar_todo(self):
        for v in [self.ventana_principal, self.ventana_ajustes,
                  self.ventana_viajes, self.ventana_detalle, self.ventana_compra]:
            if v:
                v.close()

    # ── Paquetes ─────────────────────────────────────────────────────────────

    def ver_pedido(self, pedido_id: int):
        from src.vista.VentanaDetalleMViaje import VentanaDetalleMViaje
        pedido = PedidoDAO().obtener_por_paquete(pedido_id)
        if not pedido:
            return
        self.ventana_detalle = VentanaDetalleMViaje(self.user, pedido)
        self.ventana_detalle.show()
        self._ocultar_todas_menos(self.ventana_detalle)
    
    
    def ver_paquete(self, paquete_id: int):
        from src.modelo.dao.PaqueteDAO import PaqueteDAO
        from src.vista.VentanaDetallePaquete import VentanaDetallePaquete

        paquete = PaqueteDAO().obtener_por_id(paquete_id)
        if not paquete:
            return

        self.ventana_detalle = VentanaDetallePaquete(self.user, paquete)
        self.ventana_detalle.show()
        self._ocultar_todas_menos(self.ventana_detalle)

    def abrir_ventana_compra(self, paquete: dict):
        from src.vista.VentanaCompra import VentanaCompra
        self.ventana_compra = VentanaCompra(paquete, self.user)
        self.ventana_compra.show()

    # ── Pedidos ──────────────────────────────────────────────────────────────

    def obtener_viajes_cliente(self) -> list[dict]:
        """Devuelve todos los pedidos del usuario actual."""
        return PedidoDAO().obtener_por_cliente(self.user.usuario_id)

    def comprar_paquete(self, paquete: dict, fecha_inicio, fecha_fin,
                        personas: int, metodo_pago: str) -> tuple[bool, str]:
        if fecha_fin <= fecha_inicio:
            return False, "La fecha de fin debe ser posterior a la de inicio."
        if personas < 1:
            return False, "Debe haber al menos 1 persona."
        if not metodo_pago:
            return False, "Selecciona un método de pago."

        try:
            precio_unitario = float(paquete.get("precio", 0))
        except ValueError:
            return False, "El paquete no tiene un precio válido."

        monto_total = precio_unitario * personas

        vo = PedidoVO(
            cliente_id=self.user.usuario_id,
            paquete_id=paquete.get("id") or paquete.get("paquete_id"),
            monto_total=monto_total,
            metodo_pago=metodo_pago,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        pedido_id = PedidoDAO().insertar_pedido(vo)
        if pedido_id is None:
            return False, "No se pudo registrar el pedido. Inténtalo de nuevo."

        return True, f"¡Reserva confirmada! Tu número de pedido es #{pedido_id}."

    # ── Perfil ───────────────────────────────────────────────────────────────

    def guardar_perfil(self, telefono: str, preferencia: str, preferencia_acc: str):
        dao = CuentaDAO()
        ok_tel  = dao.actualizarTelefono(self.user.usuario_id, telefono)
        ok_pref = dao.actualizarPreferencia(self.user.usuario_id, preferencia)
        ok_acc  = dao.actualizarPreferenciaAccesibilidad(
                      self.user.usuario_id, preferencia_acc)

        if ok_tel and ok_pref and ok_acc:
            self.user = UserDAO().obtenerUsuarioPorId(self.user.usuario_id)
            return True
        return False

    def cambiar_contrasena(self, pass_actual: str, pass_nueva: str, pass_confirmar: str):        
        loginVO = LoginVO(self.user.email, pass_actual)
        user_check = UserDAO().consultaLogin(loginVO)
        exito = False
        if not user_check:
            return False, 'contraseña incorrecta'
        
        exito = UserDAO().actualizarContrasena(self.user.usuario_id, pass_nueva)
        return exito
        
