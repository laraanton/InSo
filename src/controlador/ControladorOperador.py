from __future__ import annotations
import csv
import os
from datetime import date, timedelta

from src.modelo.dao.PaqueteDAO  import PaqueteDAO
from src.modelo.dao.ReservaDAO  import ReservaDAO
from src.modelo.dao.AnalisisDAO import AnalisisDAO

class ControladorOperador:
    def __init__(self, usuario_id: int | None = None):
        self._usuario_id = usuario_id
        self._paq = PaqueteDAO()
        self._res = ReservaDAO()
        self._ana = AnalisisDAO()

    # Req_27 · VentanaDiseno – crear paquete

    def crear_paquete(self, datos: dict) -> tuple[bool, str]:
        ok, msg = self._validar_paquete(datos)
        if not ok:
            return False, msg

        nuevo_id = self._paq.insertar(datos, operador_id=self._usuario_id)
        if nuevo_id is None:
            return False, "Error al guardar el paquete en la base de datos."

        self._paq.registrar_historial(
            nuevo_id, self._usuario_id,
            f"Paquete '{datos['nombre']}' creado."
        )
        return True, f"Paquete '{datos['nombre']}' guardado correctamente (ID {nuevo_id})."

    # Req_27 · VentanaEditar – listar, editar y eliminar

    def obtener_todos(self) -> list[dict]:
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


    # Req_25 / Req_26 · VentanaCompra – reservas

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
                f.write(",".join(cabecera_visible) + "\n")
                writer = csv.DictWriter(
                    f, fieldnames=campos_bd, extrasaction="ignore"
                )
                writer.writerows(reservas)

            return True, f"Exportado correctamente en: {ruta}"
        except Exception as e:
            return False, f"Error al exportar: {e}"

    # Req_28 · VentanaAnalisis – análisis de venta

    def get_datos_analisis(self, periodo: str) -> dict:
        fecha_desde = self._resolver_fecha_desde(periodo)
        # ── KPIs 
        kpis = self._ana.kpis_resumen(fecha_desde)

        ingresos_raw = kpis.get("ingresos_totales") or 0.0
        kpi_ingresos = f"{ingresos_raw:,.0f} €".replace(",", ".")

        kpi_pedidos = str(kpis.get("total_pedidos") or 0)

        satisf_raw = kpis.get("satisfaccion_media")
        kpi_satisf = f"{satisf_raw:.1f} / 5" if satisf_raw is not None else "— / 5"

        kpi_reclam = str(kpis.get("total_reclamaciones") or 0)

        # ── Datos de gráficos 
        return {
            "kpi_ingresos":   kpi_ingresos,
            "kpi_pedidos":    kpi_pedidos,
            "kpi_satisf":     kpi_satisf,
            "kpi_reclam":     kpi_reclam,
            "ventas_paquete": self._ana.ventas_por_paquete(fecha_desde),
            "ingresos_mes":   self._ana.ingresos_por_mes(fecha_desde),
            "estado_pedidos": self._ana.distribucion_estados(fecha_desde),
            "satisfaccion":   self._ana.satisfaccion_por_paquete(fecha_desde),
            "reclamaciones":  self._ana.reclamaciones_por_categoria(fecha_desde),
            "perfil_viajero": self._ana.distribucion_perfiles(),
        }

    def exportar_analisis(self, periodo: str) -> tuple[bool, str]:
        try:
            fecha_desde = self._resolver_fecha_desde(periodo)
            filas = self._ana.exportar_resumen(fecha_desde)

            if not filas:
                return False, "No hay datos para exportar en el período seleccionado."

            # Nombre de archivo seguro para cualquier SO
            slug = (
                periodo.lower()
                .replace(" ", "_")
                .replace("á", "a").replace("é", "e")
                .replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
            nombre_archivo = f"analisis_{slug}_{date.today().isoformat()}.csv"
            ruta = os.path.join(os.path.expanduser("~"), "Documents", nombre_archivo)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)

            cabeceras_visibles = [
                "ID Pedido", "Cliente", "Paquete",
                "Fecha", "Monto (€)", "Estado",
                "Val. Trato Operador", "Val. Transporte",
                "Val. Alojamiento", "Val. General",
                "Categoría Reclamación",
            ]
            campos_bd = [
                "id_pedido", "cliente", "paquete",
                "fecha", "monto", "estado",
                "val_trato", "val_transporte",
                "val_alojamiento", "val_general",
                "categoria_reclamacion",
            ]

            with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
                f.write(",".join(cabeceras_visibles) + "\n")
                writer = csv.DictWriter(
                    f, fieldnames=campos_bd, extrasaction="ignore"
                )
                writer.writerows(filas)

            return True, f"Exportado correctamente en: {ruta}"

        except Exception as exc:
            return False, f"Error al exportar: {exc}"

    # 
    # Helpers privados

    @staticmethod
    def _resolver_fecha_desde(periodo: str) -> date | None:
        hoy = date.today()
        mapping = {
            "Últimos 30 días": hoy - timedelta(days=30),
            "Últimos 3 meses": hoy - timedelta(days=90),
            "Últimos 6 meses": hoy - timedelta(days=180),
            "Este año":        date(hoy.year, 1, 1),
        }
        return mapping.get(periodo)

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
