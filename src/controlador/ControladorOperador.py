from __future__ import annotations
import csv
import os
from datetime import date, timedelta

from src.modelo.dao.PaqueteDAO  import PaqueteDAO
from src.modelo.dao.ReservaDAO  import ReservaDAO
from src.modelo.dao.AnalisisDAO import AnalisisDAO
from src.modelo.dao.FeedbackDAO  import FeedbackDAO
from src.modelo.dao.ReclamacionDAO  import ReclamacionDAO

class ControladorOperador:
    def __init__(self, usuario_id= None):
        self._usuario_id = usuario_id #Guarda quien es el usuario conectado
        self._paq = PaqueteDAO()
        self._res = ReservaDAO()
        self._ana = AnalisisDAO()
        self._feed= FeedbackDAO()
        self._rec= ReclamacionDAO()

    #-----------GESTIÓN DE PAQUETES------------------

    def crear_paquete(self, datos):
        #1 Validar datos
        ok, msg = self._validar_paquete(datos)
        if not ok:
            return False, msg
        #2 Guardar en la BD
        nuevo_id = self._paq.insertar(datos, operador_id=self._usuario_id)
        if nuevo_id is None: #Error en la BD
            return False, "Error al guardar el paquete en la base de datos."
        
        #3 Historial
        self._paq.registrar_historial(
            nuevo_id, self._usuario_id,
            f"Paquete '{datos['nombre']}' creado."
        )
        return True, f"Paquete '{datos['nombre']}' guardado correctamente (ID {nuevo_id})."

    def obtener_todos(self):
        return self._paq.obtener_todos()

    def obtener_por_id(self, id_paquete):
        return self._paq.obtener_por_id(id_paquete)

    def editar_paquete(self, id_paquete, datos):
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

    def eliminar_paquete(self, id_paquete):
        #Protección de integridad
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

    # ---------- GESTIÓN DE RESERVAS --------------------

    def obtener_reservas(self):
        return self._res.obtener_todas()

    def buscar_reservas(self, texto: str = "", estado: str = ""):
        return self._res.buscar(texto=texto, estado=estado)

    def cambiar_estado_reserva(self, id_pedido, nuevo_estado):
        estados_validos = {
            "Pendiente confirmacion", "Confirmado", "Pagado",
            "En curso", "Finalizado", "Cancelado", "Reembolsado",
        }
        if nuevo_estado not in estados_validos:
            return False, f"Estado '{nuevo_estado}' no reconocido."

        #Evitar problemas en la BD
        reserva  = self._res.obtener_por_identificador(id_pedido)
        if reserva and reserva.get("estado") == "Finalizado":
            return False, f"Pedido {id_pedido} ya está finalizado y no se puede modificar."
        
        ok = self._res.actualizar_estado(
            id_pedido, nuevo_estado, usuario_id=self._usuario_id
        )
        if not ok:
            return False, f"Pedido {id_pedido} no encontrado o error en BD."
        return True, f"Pedido {id_pedido} → '{nuevo_estado}'."

    def registrar_reserva(self, datos):
        #1 Valida cliente especificado
        if not datos.get("cliente_id"):
            return False, "El campo 'cliente_id' es obligatorio."
        
        #2 Valida paquete especificado
        if not datos.get("paquete_id"):
            return False, "El campo 'paquete_id' es obligatorio."

        #3 Inyecta el operador en el dict antes de enviarlo al DAO
        datos["usuario_responsable"] = self._usuario_id

        #4 DAO inserta la reserva y devuelve el id generado
        identificador = self._res.insertar(datos)
        if identificador is None:
            return False, "Error al crear la reserva en la base de datos."
        return True, f"Reserva {identificador} creada correctamente."

    def exportar_csv(self, ruta):
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


    # -------------- ANÁLISIS DE VENTA ------------------

    def get_datos_analisis(self, periodo: str) -> dict:
        #Convierte el texto del QComboBox en una fecha real para filtrar la BD
        fecha_desde = self._resolver_fecha_desde(periodo)

        #Obtiene los cuatro KPIs resumidos del DAO en un solo dict
        kpis = self._ana.kpis_resumen(fecha_desde)

        #Extrae ingresos totales del dict
        ingresos_raw = kpis.get("ingresos_totales") or 0.0

        # Formatea el número como moneda europea: 14320.0 -> "14.320 €"
        # :,.0f añade separadores de miles con coma, .replace los cambia a punto
        kpi_ingresos = f"{ingresos_raw:,.0f} €".replace(",", ".")

        # Conviertir total pedidos a string para mostrarlo en un QLabel
        kpi_pedidos = str(kpis.get("total_pedidos") or 0)

        # Extrae la media de satisfacción; puede ser None si no hay valoraciones
        satisf_raw = kpis.get("satisfaccion_media")

        # Si hay datos muestra "4.2 / 5", si no hay datos muestra "— / 5"
        kpi_satisf = f"{satisf_raw:.1f} / 5" if satisf_raw is not None else "— / 5"

        # Convierte el total de reclamaciones a string para el QLabel
        kpi_reclam = str(kpis.get("total_reclamaciones") or 0)

        # Devuelve un único dict con KPIs y datos de los seis gráficos
        # VentanaAnalisis los distribuye sin hacer ningún cálculo adicional
        return {
            # KPIs para las cuatro cajitas superiores de la ventana
            "kpi_ingresos":   kpi_ingresos,
            "kpi_pedidos":    kpi_pedidos,
            "kpi_satisf":     kpi_satisf,
            "kpi_reclam":     kpi_reclam,

            # Datos para el gráfico de barras: ventas por paquete
            "ventas_paquete": self._ana.ventas_por_paquete(fecha_desde),

            # Datos para el gráfico de líneas: ingresos mes a mes
            "ingresos_mes":   self._ana.ingresos_por_mes(fecha_desde),

            # Datos para el gráfico de tarta: distribución de estados de pedidos
            "estado_pedidos": self._ana.distribucion_estados(fecha_desde),

            # Datos para el gráfico de barras: nota media por paquete
            "satisfaccion":   self._ana.satisfaccion_por_paquete(fecha_desde),

            # Datos para el gráfico de barras: reclamaciones por categoría
            "reclamaciones":  self._ana.reclamaciones_por_categoria(fecha_desde),

            # Datos para el gráfico de tarta: tipo de viajero (sin filtro de fecha)
            "perfil_viajero": self._ana.distribucion_perfiles(),
        }
    
    def exportar_analisis(self, periodo):
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
                "ID Pedido", "Cliente", "Paquete", "Fecha", "Monto (€)", "Estado", "Val. Trato Operador", "Val. Transporte","Val. Alojamiento", "Val. General",
                "Categoría Reclamación",
            ]
            campos_bd = [
                "id_pedido", "cliente", "paquete", "fecha", "monto", "estado", "val_trato", "val_transporte", "val_alojamiento", "val_general", "categoria_reclamacion",
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
    
    # -------------- FEEDBACK ------------------
    def obtener_feedbacks(self) -> list[dict]:
        return self._feed.obtener_todos()
    
    def buscar_feedbacks(self, texto="", paquete="") -> list[dict]:
        return self._feed.buscar(texto=texto, paquete=paquete)

    def obtener_paquetes_con_feedback(self) -> list[str]:
        return self._feed.obtener_paquetes_con_feedback()

    # -------------- RECLAMACIONES ------------------

    def obtener_reclamaciones(self) -> list[dict]:
            return self._rec.obtener_todas()

    def buscar_reclamaciones(self, texto="", categoria="", estado="") -> list[dict]:
        return self._rec.buscar(texto=texto, categoria=categoria, estado=estado)

    def cambiar_estado_reclamacion(self, reclamacion_id: int,
                                    nuevo_estado: str) -> tuple[bool, str]:
        estados_validos = {
            "Registrada", "En revisión", "En gestión", "Resuelta", "Rechazada", "Cerrada",
        }
        if nuevo_estado not in estados_validos:
            return False, f"Estado '{nuevo_estado}' no reconocido."
        ok = self._rec.actualizar_estado(reclamacion_id, nuevo_estado)
        if not ok:
            return False, "Error al actualizar el estado en la base de datos."
        return True, f"Estado actualizado a '{nuevo_estado}'."

    # Helpers privados

    @staticmethod
    def _resolver_fecha_desde(periodo: str) -> date | None:
        hoy = date.today()
        mapping = {
            "Últimos 30 días": hoy - timedelta(days=30),
            "Últimos 3 meses": hoy - timedelta(days=90),
            "Últimos 6 meses": hoy - timedelta(days=180),
            "Este año": date(hoy.year, 1, 1),
        }
        return mapping.get(periodo)

    @staticmethod
    def _validar_paquete(datos: dict) -> tuple[bool, str]:
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
