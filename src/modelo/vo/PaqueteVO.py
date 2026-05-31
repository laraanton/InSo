class PaqueteVO:
    def __init__(self, id, nombre, destino, duracion, precio,
                 descripcion="", servicios="", perfil="General",
                 accesibilidad=False, fecha_ini="", fecha_fin="",
                 estado_paquete="Activo", creado_por=None, fecha_creacion=""):
        self.id             = id
        self.nombre         = nombre
        self.destino        = destino
        self.duracion       = duracion
        self.precio         = precio
        self.descripcion    = descripcion
        self.servicios      = servicios
        self.perfil         = perfil
        self.accesibilidad  = accesibilidad
        self.fecha_ini      = fecha_ini
        self.fecha_fin      = fecha_fin
        self.estado_paquete = estado_paquete
        self.creado_por     = creado_por
        self.fecha_creacion = fecha_creacion

    @staticmethod
    def from_row(row):
        # Orden columnas (_SELECT de PaqueteDAO):
        # 0 paquete_id, 1 nombre_paquete, 2 descripcion_detallada, 3 destino,
        # 4 duracion_dias, 5 precio_tpv, 6 servicios_incluidos, 7 perfil_objetivo,
        # 8 accesibilidad_certificada, 9 creado_por_operador,
        # 10 fecha_creacion, 11 estado_paquete
        return PaqueteVO(
            id             = row[0],
            nombre         = row[1]  or "",
            descripcion    = row[2]  or "",
            destino        = row[3]  or "",
            duracion       = str(row[4]) if row[4] is not None else "",
            precio         = str(row[5]) if row[5] is not None else "",
            servicios      = row[6]  or "",
            perfil         = row[7]  or "General",
            accesibilidad  = bool(row[8]),
            creado_por     = row[9],
            fecha_creacion = row[10] or "",
            estado_paquete = row[11] or "Activo",
        )
        
    @staticmethod
    def from_dict(d: dict) -> "PaqueteVO":
        return PaqueteVO(
            id=d.get("id"),
            nombre=d.get("nombre", ""),
            destino=d.get("destino", ""),
            duracion=d.get("duracion", ""),
            precio=d.get("precio", ""),
            descripcion=d.get("descripcion", ""),
            servicios=d.get("servicios", ""),
            perfil=d.get("perfil", "General"),
            accesibilidad=d.get("accesibilidad", False),
            fecha_ini=d.get("fecha_ini", ""),
            fecha_fin=d.get("fecha_fin", ""),
        )
        
    def to_insert_params(self, operador_id=None):
        return [
            self.nombre.strip(),
            self.descripcion.strip(),
            self.destino.strip(),
            _to_int(self.duracion),
            _to_float(self.precio),
            self.servicios.strip(),
            self.perfil.strip(),
            1 if self.accesibilidad else 0,
            operador_id,
        ]

    def to_update_params(self, paquete_id):
        return [
            self.nombre.strip(),
            self.descripcion.strip(),
            self.destino.strip(),
            _to_int(self.duracion),
            _to_float(self.precio),
            self.servicios.strip(),
            self.perfil.strip(),
            1 if self.accesibilidad else 0,
            paquete_id,
        ]

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "nombre":        self.nombre,
            "destino":       self.destino,
            "duracion":      self.duracion,
            "precio":        self.precio,
            "descripcion":   self.descripcion,
            "servicios":     self.servicios,
            "perfil":        self.perfil,
            "accesibilidad": self.accesibilidad,
            "fecha_ini":     self.fecha_ini,
            "fecha_fin":     self.fecha_fin,
            "estado_paquete": self.estado_paquete,
        }


def _to_int(valor, defecto=1):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return defecto


def _to_float(valor, defecto=0.0):
    try:
        return float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        return defecto
