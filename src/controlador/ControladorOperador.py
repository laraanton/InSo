"""
ControladorOperador.py
======================
Controlador MVC único para las tres vistas del módulo Operador:

    VentanaDiseno  → crear_paquete()
    VentanaEditar  → obtener_todos(), obtener_por_id(),
                     editar_paquete(), eliminar_paquete()
    VentanaCompra  → buscar_reservas(), cambiar_estado_reserva(),
                     registrar_reserva(), exportar_csv()

Ninguna Vista accede a la BD directamente.  Siempre llaman aquí.

Flujo MVC:
    Vista  ──▶  ControladorOperador  ──▶  DAO  ──▶  BD (SQL Server)
      ◀──────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import csv
from datetime import date

from src.modelo.dao.PaqueteDAO import PaqueteDAO
from src.modelo.dao.ReservaDAO import ReservaDAO


class ControladorOperador:
    """
    Punto de entrada único para la lógica de negocio del Operador.

    Instanciar en cada Vista:
        self._ctrl = ControladorOperador()
        ok, msg = self._ctrl.crear_paquete(datos)

    El usuario en sesión puede inyectarse opcionalmente para
    mantener la trazabilidad en los historiales:
        self._ctrl = ControladorOperador(usuario_id=user.usuario_id)
    """

    def __init__(self, usuario_id: int | None = None):
        self._usuario_id = usuario_id
        self._paq = PaqueteDAO()
        self._res = ReservaDAO()

    # ═══════════════════════════════════════════════════════════════════════
    # Req_27 · VentanaDiseno – crear paquete
    # ═══════════════════════════════════════════════════════════════════════

    def crear_paquete(self, datos: dict) -> tuple[bool, str]:
        """
        Valida y persiste un paquete nuevo (Req_27).

        Campos esperados en `datos`:
            nombre*, destino*, duracion, precio*,
            descripcion, servicios, perfil,
            accesibilidad, fecha_ini, fecha_fin
        (*) obligatorios según ERS § 2.2.4
        """
        ok, msg = self._validar_paquete(datos)
        if not ok:
            return False, msg

        nuevo_id = self._paq.insertar(datos, operador_id=self._usuario_id)
        if nuevo_id is None:
            return False, "Error al guardar el paquete en la base de datos."

        # Historial de creación
        self._paq.registrar_historial(
            nuevo_id, self._usuario_id,
            f"Paquete '{datos['nombre']}' creado."
        )
        return True, f"Paquete '{datos['nombre']}' guardado correctamente (ID {nuevo_id})."

    # ═══════════════════════════════════════════════════════════════════════
    # Req_27 · VentanaEditar – listar, editar y eliminar
    # ═══════════════════════════════════════════════════════════════════════

    def obtener_todos(self) -> list[dict]:
        """
        Devuelve todos los paquetes activos.
        Usado por VentanaEditar (lista lateral) y VentanaCompra (catálogo).
        """
        return self._paq.obtener_todos()

    def obtener_por_id(self, id_paquete: int) -> dict | None:
        """Devuelve un paquete concreto o None si no existe."""
        return self._paq.obtener_por_id(id_paquete)

    def editar_paquete(self, id_paquete: int, datos: dict) -> tuple[bool, str]:
        """
        Valida y actualiza un paquete existente (Req_27).
        VentanaEditar lo llama al pulsar 'Guardar cambios'.
        """
        ok, msg = self._validar_paquete(datos)
        if not ok:
            return False, msg

        if not self._paq.actualizar(id_paquete, datos):
            return False, "Error al actualizar el paquete en la base de datos."

        self._paq.registrar_historial(
            id_paquete, self._usuario_id,
            f"Paquete actualizado: {datos['nombre']}."
        )
        return True, f"Paquete '{datos['nombre']}' actualizado correctamente."

    def eliminar_paquete(self, id_paquete: int) -> tuple[bool, str]:
        """
        Elimina (borrado lógico) un paquete (Req_27).
        Comprueba que no existan reservas activas antes de proceder.
        """
        if self._paq.tiene_reservas_activas(id_paquete):
            return False, "No se puede eliminar: el paquete tiene reservas activas."

        paq = self._paq.obtener_por_id(id_paquete)
        if paq is None:
            return False, "Paquete no encontrado."

        if not self._paq.eliminar(id_paquete):
            return False, "Error al eliminar el paquete en la base de datos."

        self._paq.registrar_historial(
            id_paquete, self._usuario_id,
            f"Paquete '{paq['nombre']}' marcado como Inactivo (eliminado)."
        )
        return True, f"Paquete '{paq['nombre']}' eliminado correctamente."

    # ═══════════════════════════════════════════════════════════════════════
    # Req_25 / Req_26 · VentanaCompra – reservas
    # ═══════════════════════════════════════════════════════════════════════

    def obtener_reservas(self) -> list[dict]:
        """
        Devuelve todas las reservas con nombre de cliente y paquete (Req_25).
        Cada dict: id, cliente, paquete, fecha, precio, estado.
        """
        return self._res.obtener_todas()

    def buscar_reservas(self, texto: str = "", estado: str = "") -> list[dict]:
        """
        Filtra reservas por texto libre y/o estado (Req_23, Req_26).
        VentanaCompra lo llama en inputBuscar y comboEstado.
        """
        return self._res.buscar(texto=texto, estado=estado)

    def cambiar_estado_reserva(self, id_pedido: str,
                               nuevo_estado: str) -> tuple[bool, str]:
        """
        Actualiza el estado de una reserva y registra el historial (Req_26).
        VentanaCompra lo llama desde el combo de cada fila.
        """
        estados_validos = {
            "Pendiente confirmacion", "Confirmado", "Pagado",
            "En curso", "Finalizado", "Cancelado", "Reembolsado",
        }
        if nuevo_estado not in estados_validos:
            return False, f"Estado '{nuevo_estado}' no reconocido."

        ok = self._res.actualizar_estado(
            id_pedido, nuevo_estado, usuario_id=self._usuario_id
        )
        if not ok:
            return False, f"Pedido {id_pedido} no encontrado o error en BD."
        return True, f"Pedido {id_pedido} → '{nuevo_estado}'."

    def registrar_reserva(self, datos: dict) -> tuple[bool, str]:
        """
        Crea una nueva reserva (Req_25).

        datos esperados:
            cliente_id*  (int),  paquete_id*  (int),
            monto_total* (float),
            metodo_pago  (str),
            fecha_inicio (str YYYY-MM-DD, opcional),
            fecha_fin    (str YYYY-MM-DD, opcional)

        Para crear reservas desde la interfaz, abrir primero un diálogo
        que resuelva cliente_id y paquete_id a partir de los nombres.
        """
        if not datos.get("cliente_id"):
            return False, "El campo 'cliente_id' es obligatorio."
        if not datos.get("paquete_id"):
            return False, "El campo 'paquete_id' es obligatorio."

        datos["usuario_responsable"] = self._usuario_id
        identificador = self._res.insertar(datos)
        if identificador is None:
            return False, "Error al crear la reserva en la base de datos."
        return True, f"Reserva {identificador} creada correctamente."

    def exportar_csv(self, ruta: str) -> tuple[bool, str]:
        """
        Exporta todas las reservas a un archivo CSV (Req_19).
        VentanaCompra lo llama desde btnExportar.
        """
        try:
            reservas = self._res.exportar_todas()
            cabecera_visible = ["ID Pedido", "Cliente", "Paquete",
                                "Fecha", "Precio", "Estado", "Método Pago"]
            campos_bd = ["id", "cliente", "paquete",
                         "fecha", "precio", "estado", "metodo_pago"]

            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                # utf-8-sig para que Excel reconozca la codificación
                f.write(",".join(cabecera_visible) + "\n")
                writer = csv.DictWriter(
                    f, fieldnames=campos_bd, extrasaction="ignore"
                )
                writer.writerows(reservas)

            return True, f"Exportado correctamente en: {ruta}"
        except Exception as e:
            return False, f"Error al exportar: {e}"

    # ═══════════════════════════════════════════════════════════════════════
    # Validaciones privadas
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _validar_paquete(datos: dict) -> tuple[bool, str]:
        """Comprueba campos obligatorios (Req_27, ERS § 2.2.4)."""
        if not datos.get("nombre", "").strip():
            return False, "El campo 'Nombre del paquete' es obligatorio."
        if not datos.get("destino", "").strip():
            return False, "El campo 'Destino' es obligatorio."

        precio_str = datos.get("precio", "").strip()
        if not precio_str:
            return False, "El campo 'Precio (TPV)' es obligatorio."
        try:
            if float(precio_str.replace(",", ".")) <= 0:
                raise ValueError
        except ValueError:
            return False, "El precio debe ser un número positivo (ej: 1200.00)."

        return True, ""
