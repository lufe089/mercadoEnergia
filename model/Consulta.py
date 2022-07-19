from datetime import datetime, timedelta


class Consulta:

    def __init__(self):
        self.nombre_metrica = ""
        self.coleccion_id = ""
        self.agente= ""
        self.fecha_inicial = datetime.today() - timedelta(29)
        self.fecha_final = datetime.today()
        self.tipo_metrica = ""
        self.resultados_busqueda =None
        self.is_agrupar_x_dia_gui = False
        self.is_agrupar_x_mes_gui = False
        self.opc_agrup_result = None
        self.metricas = {}
        self.metrica_seleccionada_id = ""
        self.metrica_selecccionada = None


    def es_consulta_horaria(self):
        """ Identifica si la consulta es horaria pues segun eso la GUI pintara algo diferente"""
        if self.metricas[self.metrica_seleccionada_id].tipo_metrica  == "Horaria":
            return True
        else:
            return False