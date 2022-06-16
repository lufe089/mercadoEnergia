import requests
import json
import pandas as pd
import datetime as dt

from model.Coleccion import Coleccion
from model.Metrica import Metrica


class MercadoController:
    def __init__(self) -> None:
        super().__init__()
        self.coleccion_info_dic = {}

    def construir_info_metricas(self):
        url = f'http://servapibi.xm.com.co/lists'
        request = {'MetricId': "ListadoMetricas",
                    'Entity': "Sistema"}

        connection = requests.post(url, json=request)
        data_json = json.loads(connection.content)
        df_colecciones = pd.json_normalize(data_json['Items'], 'ListEntities', 'Date', sep='_')
        print(df_colecciones)

        for i in range(len(df_colecciones)):
            metricaTemp= Coleccion(nombre_coleccion= df_colecciones.loc[i,"Values_MetricName"],
                    max_dias= df_colecciones.loc[i,"Values_MaxDays"],
                    id_coleccion= df_colecciones.loc[i,"Values_MetricId"], unidades_metrica= df_colecciones.loc[i,"Values_MetricUnits"], descripcion= df_colecciones.loc[i,"Values_MetricDescription"], query_url = df_colecciones.loc[i,"Values_Url"])
            self.coleccion_info_dic[metricaTemp.id_coleccion] = metricaTemp


    def sumar_valores_hora(self, fila):
        """ Suma las columnas relacionadas con las horas y retorna el valor diario"""
        suma = 0.0

        # Suma las columnas de  las horas desde la hora 1 hasta la hora 24 aprovechando el indice que propone pandas
        for i in range(2, 26):
            # Algunos de los datos no son de tipo entero por ejemplo hay N/A en ese caso no se suman
            if  isinstance(fila[i],int) or isinstance(fila[i],float) :
                suma = suma + fila[i]
        return suma

    def agrupar_horas_dias(self,input_df):
        # Limpiar datos para quitar NaN
        output_df = input_df.fillna(value=0)

        # Eje 1 significa que se reciben las filas
        output_df["Value"] = output_df.apply(self.sumar_valores_hora, axis=1)

        # Quitar la parte de la hora del campo fecha
        output_df['Date'] = output_df['Date'].apply(lambda x: x.strftime("%m/%d/%Y"))
        # Guardar el resumen de los datos diarios

        # Values_code tiene el codigo que indica el elemento principal de consulta
        output_df = output_df[['Values_code', 'Date', 'Value']]

        # Poner la fecha como el indice
        # output_df.set_index('Date', inplace=True)
        return output_df