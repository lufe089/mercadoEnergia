class Coleccion:

    def __init__(self, id_coleccion, nombre_coleccion, unidades_metrica, descripcion, query_url, max_dias):
        self.descripcion = descripcion
        self.unidades_metrica = unidades_metrica
        self.max_dias = max_dias
        self.nombre_coleccion = nombre_coleccion
        self.id_coleccion = id_coleccion
        self.query_url = query_url

    def __str__(self) -> str:
        return f"*{self.nombre_coleccion}*: {self.descripcion}\n * Unidad de valor consulta: {self.unidades_metrica}\n * Max días consulta: {self.max_dias}"

