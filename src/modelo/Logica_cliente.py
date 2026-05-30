from src.modelo.dao.UserDAO import UserDAO
from src.modelo.dao.CuentaDAO import CuentaDAO
from src.modelo.dao.PedidoDAO import PedidoDAO
from src.modelo.dao.PaqueteDAO import PaqueteDAO
from src.modelo.vo.LoginVO import LoginVO
from src.modelo.vo.PedidoVO import PedidoVO
from src.modelo.vo.PaqueteVO import PaqueteVO
from src.modelo.EstrategiaPago import obtener_estrategia, nombres_disponibles


class BusinessCliente:
    def __init__(self):
        self._paq = PaqueteDAO()
        self._ped = PedidoDAO()
        self._usr = UserDAO()
        self._cta = CuentaDAO()

    # ── Paquetes ─────────────────────────────────────────────────────────────

    def obtener_todos_paquetes(self) -> list[dict]:
        return [p.to_dict() for p in self._paq.obtener_todos()]

    def obtener_paquete_por_id(self, id_paquete: int) -> dict | None:
        vo = self._paq.obtener_por_id(id_paquete)
        return vo.to_dict() if vo else None

    # ── Pedidos ──────────────────────────────────────────────────────────────

    def obtener_viajes_cliente(self, usuario_id: int) -> list[dict]:
        return self._ped.obtener_por_cliente(usuario_id)

    def obtener_pedido(self, pedido_id: int) -> dict | None:
        return self._ped.obtener_por_paquete(pedido_id)

    def comprar_paquete(self, usuario_id: int, paquete: dict,
                        fecha_inicio, fecha_fin,
                        personas: int, metodo_pago: str) -> tuple[bool, str]:
        # ── Validaciones de negocio ──────────────────────────────────────────
        if fecha_fin <= fecha_inicio:
            return False, "La fecha de fin debe ser posterior a la de inicio."
        if personas < 1:
            return False, "Debe haber al menos 1 persona."
        if not metodo_pago:
            return False, "Selecciona un método de pago."

        try:
            precio_unitario = float(paquete.get("precio", 0))
        except (ValueError, TypeError):
            return False, "El paquete no tiene un precio válido."

        monto_total = precio_unitario * personas

        # ── Estrategia de pago ───────────────────────────────────────────────
        estrategia = obtener_estrategia(metodo_pago)
        if not estrategia:
            return False, f"Método de pago '{metodo_pago}' no reconocido."

        ok, msg_validacion = estrategia.validar(monto_total)
        if not ok:
            return False, msg_validacion

        # ── Persistencia ─────────────────────────────────────────────────────
        vo = PedidoVO(
            cliente_id=usuario_id,
            paquete_id=paquete.get("id") or paquete.get("paquete_id"),
            monto_total=monto_total,
            metodo_pago=metodo_pago,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        pedido_id = self._ped.insertar_pedido(vo)
        if pedido_id is None:
            return False, "No se pudo registrar el pedido. Inténtalo de nuevo."

        # ── Procesamiento del pago ───────────────────────────────────────────
        ok, msg_pago = estrategia.procesar(monto_total)
        if not ok:
            return False, msg_pago

        return True, (
            f"¡Reserva confirmada! Tu número de pedido es #{pedido_id}.\n\n"
            f"{msg_pago}"
        )

    def obtener_metodos_pago(self) -> list[str]:
        return nombres_disponibles()

    # ── Perfil ───────────────────────────────────────────────────────────────

    def guardar_perfil(self, usuario_id: int,
                       telefono: str, preferencia: str,
                       preferencia_acc: str) -> tuple[bool, str]:
        ok_tel  = self._cta.actualizarTelefono(usuario_id, telefono)
        ok_pref = self._cta.actualizarPreferencia(usuario_id, preferencia)
        ok_acc  = self._cta.actualizarPreferenciaAccesibilidad(usuario_id, preferencia_acc)

        if ok_tel and ok_pref and ok_acc:
            return True, "Perfil actualizado correctamente."
        return False, "No se pudo actualizar algún dato del perfil."

    def cambiar_contrasena(self, usuario_id: int, email: str,
                           pass_actual: str, pass_nueva: str) -> tuple[bool, str]:
        login_vo = LoginVO(email, pass_actual)
        if not self._usr.consultaLogin(login_vo):
            return False, "La contraseña actual es incorrecta."

        if self._usr.actualizarContrasena(usuario_id, pass_nueva):
            return True, "Contraseña actualizada correctamente."
        return False, "No se pudo actualizar la contraseña."

    def refrescar_usuario(self, usuario_id: int):
        return self._usr.obtenerUsuarioPorId(usuario_id)
