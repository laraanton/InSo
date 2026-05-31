"""
Patrón Estrategia – Métodos de pago
====================================
Ubicación: src/modelo/EstrategiaPago.py

La lógica de selección y ejecución vive en BusinessCliente.
VentanaDetallePaquete solo pasa el string del combo_pago,
igual que antes. No cambia nada en la vista.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────
#  Interfaz base
# ─────────────────────────────────────────────

class EstrategiaPago(ABC):
    """Interfaz común para todos los métodos de pago."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre legible; debe coincidir con el texto del combo_pago."""

    @abstractmethod
    def validar(self, total: float, **kwargs) -> tuple[bool, str]:
        """Valida que la operación puede realizarse."""

    @abstractmethod
    def procesar(self, total: float, **kwargs) -> tuple[bool, str]:
        """Ejecuta el cobro / genera la confirmación."""


# ─────────────────────────────────────────────
#  Estrategias concretas
# ─────────────────────────────────────────────

class PagoEfectivo(EstrategiaPago):

    @property
    def nombre(self) -> str:
        return "Efectivo"

    def validar(self, total: float, **kwargs) -> tuple[bool, str]:
        if total <= 0:
            return False, "El importe debe ser mayor que 0 €."
        return True, ""

    def procesar(self, total: float, **kwargs) -> tuple[bool, str]:
        return True, f"Pago en efectivo de {total:,.2f} € pendiente en destino."


class PagoTarjeta(EstrategiaPago):

    @property
    def nombre(self) -> str:
        return "Tarjeta de crédito"

    def validar(self, total: float, **kwargs) -> tuple[bool, str]:
        if total <= 0:
            return False, "El importe debe ser mayor que 0 €."
        return True, ""

    def procesar(self, total: float, **kwargs) -> tuple[bool, str]:
        return True, f"Pago con tarjeta de {total:,.2f} € procesado correctamente."


class PagoTransferencia(EstrategiaPago):

    @property
    def nombre(self) -> str:
        return "Transferencia bancaria"

    def validar(self, total: float, **kwargs) -> tuple[bool, str]:
        if total <= 0:
            return False, "El importe debe ser mayor que 0 €."
        return True, ""

    def procesar(self, total: float, **kwargs) -> tuple[bool, str]:
        iban = "ES91 2100 0418 4502 0005 1332"
        return (
            True,
            f"Realiza una transferencia de {total:,.2f} € al IBAN {iban}. "
            f"El viaje se confirmará al recibir el pago.",
        )


class PagoPayPal(EstrategiaPago):

    @property
    def nombre(self) -> str:
        return "PayPal"

    def validar(self, total: float, **kwargs) -> tuple[bool, str]:
        if total <= 0:
            return False, "El importe debe ser mayor que 0 €."
        return True, ""

    def procesar(self, total: float, **kwargs) -> tuple[bool, str]:
        return True, f"Pago de {total:,.2f} € tramitado a través de PayPal."


# ─────────────────────────────────────────────
#  Registro central
# ─────────────────────────────────────────────

_ESTRATEGIAS: dict[str, EstrategiaPago] = {
    e.nombre: e
    for e in [
        PagoEfectivo(),
        PagoTarjeta(),
        PagoTransferencia(),
        PagoPayPal(),
    ]
}


def obtener_estrategia(nombre: str) -> EstrategiaPago | None:
    """Usada internamente por BusinessCliente."""
    return _ESTRATEGIAS.get(nombre)


def nombres_disponibles() -> list[str]:
    """
    Usada por ControladorCliente para devolver los métodos a la vista,
    que los pone en el combo_pago al arrancar.
    """
    return list(_ESTRATEGIAS.keys())
