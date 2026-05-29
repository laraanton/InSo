"""
AnalisisVO.py  –  Value Objects del módulo Análisis de Venta
============================================================
Contenedores de solo datos para KPIs y gráficos.
Sin lógica de negocio ni acceso a BD.
"""


class KpiVO:
    """Cuatro cifras resumen de la cabecera de análisis."""
    def __init__(self, ingresos: str, pedidos: str,
                 satisfaccion: str, reclamaciones: str):
        self.ingresos      = ingresos       # p.ej. "14.320 €"
        self.pedidos       = pedidos        # p.ej. "87"
        self.satisfaccion  = satisfaccion   # p.ej. "4.2 / 5"
        self.reclamaciones = reclamaciones  # p.ej. "5"


class AnalisisVO:
    """
    Agrupa los KPIs y los datos crudos de los seis gráficos.
    La Vista los consume directamente sin hacer ningún cálculo.

    ventas_paquete  → list[dict]  claves: 'paquete', 'ventas'
    ingresos_mes    → list[dict]  claves: 'mes', 'total'
    estado_pedidos  → list[dict]  claves: 'estado', 'cantidad'
    satisfaccion    → list[dict]  claves: 'paquete', 'media'
    reclamaciones   → list[dict]  claves: 'categoria', 'cantidad'
    perfil_viajero  → list[dict]  claves: 'perfil', 'media_presupuesto', 'cantidad'
    """
    def __init__(self, kpis: KpiVO,
                 ventas_paquete:  list,
                 ingresos_mes:    list,
                 estado_pedidos:  list,
                 satisfaccion:    list,
                 reclamaciones:   list,
                 perfil_viajero:  list):
        self.kpis            = kpis
        self.ventas_paquete  = ventas_paquete
        self.ingresos_mes    = ingresos_mes
        self.estado_pedidos  = estado_pedidos
        self.satisfaccion    = satisfaccion
        self.reclamaciones   = reclamaciones
        self.perfil_viajero  = perfil_viajero
