class Metrica:

   def __init__(self, nombre_metrica, entidad,nombre_coleccion, unidades_metrica, descripcion, query_url ):
        self.descripcion = descripcion
        self.unidades_metrica = unidades_metrica
        self.max_dias = 0
        self.nombre_metrica = nombre_metrica
        self.entidad = entidad
        self.nombre_coleccion = nombre_coleccion
        self.query_url = query_url


   def __init__(self, nombre_metrica, tipo_metrica, parametro_llamada, entidad, nombre_coleccion, metrica_idx) -> None:
        super().__init__()
        self.nombre_metrica = nombre_metrica
        self.tipo_metrica = tipo_metrica
        self.parametro_llamada = parametro_llamada
        self.entidad = entidad
        self.nombre_coleccion = nombre_coleccion
        self.metrica_idx = metrica_idx



   def __str__(self):
        return self.nombre_metrica