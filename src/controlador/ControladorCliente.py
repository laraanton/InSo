from src.modelo.Logica_login import BussinessObject
from src.modelo.Logica_cliente import BusinessCliente
from src.controlador.ControladorPrincipal import ControladorPrincipal

# Se importan también las ventanas siguientes:
# from src.vista.VentanaCliente import VentanaCliente
# from src.vista.VentanaAjustesCuenta import VentanaAjustesCuenta
# from src.vista.VentanaMisViajes import VentanaMisViajes
# from src.vista.Login import MiVentana

# Se importan localmente en las funciones donde las vaya a usar porque si no
# se me genera un circular import y provoca fallos.

class ControladorCliente:
    def __init__(self, user):
        self.user = user
        self.logica = BussinessObject()
        self.logica_cliente = BusinessCliente()
        self.ventana_principal = None
        self.ventana_ajustes   = None
        self.ventana_viajes    = None
        self.ventana_detalle   = None
        self.ventana_compra    = None
        self.ventana_resultados = None
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

    def ir_a_resultados(self, paquetes, termino, fecha, n_personas):
        from src.vista.VentanaResultados import VentanaResultados
        self.ventana_resultados = VentanaResultados(self.user, paquetes, termino, fecha, n_personas)
        self.ventana_resultados.show()
        self._ocultar_todas_menos(self.ventana_resultados)


    def ir_a_mis_viajes(self):
        from src.vista.VentanaMisViajes import VentanaMisViajes
        self.ventana_viajes = VentanaMisViajes(self.user)
        self.ventana_viajes.show()
        self._ocultar_todas_menos(self.ventana_viajes)

    def volver_a_principal(self):
        self._ocultar_todas_menos(None)
        self.abrir_principal()

    def cerrar_sesion(self):
        self._cerrar_todo()
        ctrl = ControladorPrincipal()
        ctrl.abrirIniciarSesion()

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

    def obtener_paquetes(self) -> list:
        return self.logica_cliente.obtener_todos_paquetes()

    def ver_paquete(self, paquete_id: int):
        from src.vista.VentanaDetallePaquete import VentanaDetallePaquete 
        paquete = self.logica_cliente.obtener_paquete_por_id(paquete_id)
        if not paquete:
            return
        self.ventana_detalle = VentanaDetallePaquete(self.user, paquete)
        self.ventana_detalle.show()
        self._ocultar_todas_menos(self.ventana_detalle)

# funcion para ver el paquete de viaje si lo abre desde el buscador
    def ver_paquete_buscado(self, paquete_id: int, fecha, n_personas):
        from src.vista.VentanaDetalleBuscador import VentanaDetalleBuscador 
        paquete = self.logica_cliente.obtener_paquete_por_id(paquete_id)
        if not paquete:
            return
        self.ventana_detalle = VentanaDetalleBuscador(self.user, paquete, fecha, n_personas)
        self.ventana_detalle.show()
        self._ocultar_todas_menos(self.ventana_detalle)

    def ver_pedido(self, pedido_id: int):
        from src.vista.VentanaDetalleMViaje import VentanaDetalleMViaje 
        pedido = self.logica_cliente.obtener_pedido(pedido_id)
        if not pedido:
            return
        self.ventana_detalle = VentanaDetalleMViaje(self.user, pedido)
        self.ventana_detalle.show()
        self._ocultar_todas_menos(self.ventana_detalle)

    def buscar_paquetes(self, texto: str) -> list[dict]:
        """Delega la búsqueda al modelo pasando el perfil del usuario."""
        return self.logica_cliente.buscar_paquetes(
            texto,
            getattr(self.user, "preferencia", ""),
            getattr(self.user, "preferencia_accesibilidad", ""),
        )

    # ── Pedidos ──────────────────────────────────────────────────────────────

    def obtener_viajes_cliente(self) -> list[dict]:
        return self.logica_cliente.obtener_viajes_cliente(self.user.usuario_id)

    def validar_compra(self, paquete, fecha_ini, fecha_fin,
                       personas, metodo) -> tuple[bool, str]:
        from datetime import date
        if fecha_ini < date.today():
            return False, "La fecha de inicio no puede ser anterior a hoy."
        dias = (fecha_fin - fecha_ini).days
        if dias != int(paquete.get("duracion", 0)):
            return False, "La duración del paquete no es flexible."
        if not metodo:
            return False, "Selecciona un método de pago."
        if personas < 1:
            return False, "Debe haber al menos 1 persona."
        return True, ""

    def calcular_total(self, paquete: dict, personas: int) -> float:
        try:
            return float(paquete.get("precio", 0)) * personas
        except (ValueError, TypeError):
            return 0.0

    def comprar_paquete(self, paquete, fecha_inicio, fecha_fin,
                        personas, metodo_pago) -> tuple[bool, str]:
        return self.logica_cliente.comprar_paquete(
            self.user.usuario_id, paquete,
            fecha_inicio, fecha_fin, personas, metodo_pago
        )

    def formatear_pedido(self, pedido: dict) -> dict:
        def fmt(f):
            try:
                y, m, d = str(f)[:10].split("-")
                return f"{d}/{m}/{y}"
            except Exception:
                return str(f) if f else "—"
        return {
            **pedido,
            "fecha_inicio_fmt": fmt(pedido.get("fecha_inicio", "")),
            "fecha_fin_fmt":    fmt(pedido.get("fecha_fin", "")),
            "monto_total":      float(pedido.get("monto_total", 0)),
        }

    # ── Perfil ───────────────────────────────────────────────────────────────

    def guardar_perfil(self, telefono, preferencia,
                       preferencia_acc) -> tuple[bool, str]:
        ok, msg = self.logica_cliente.guardar_perfil(
            self.user.usuario_id, telefono, preferencia, preferencia_acc
        )
        if ok:
            self.user = self.logica_cliente.refrescar_usuario(self.user.usuario_id)
        return ok, msg

    def cambiar_contrasena(self, pass_actual, pass_nueva,
                           pass_confirmar) -> tuple[bool, str]:
        if not pass_actual:
            return False, "Introduce tu contraseña actual."
        if not pass_nueva or len(pass_nueva) < 6:
            return False, "La contraseña nueva debe tener al menos 6 caracteres."
        if pass_nueva != pass_confirmar:
            return False, "Las contraseñas nuevas no coinciden."
        if pass_actual == pass_nueva:
            return False, "La nueva contraseña no puede ser igual a la actual."
        return self.logica_cliente.cambiar_contrasena(
            self.user.usuario_id, self.user.email,
            pass_actual, pass_nueva
        )
