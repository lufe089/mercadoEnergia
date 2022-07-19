import requests
import json
import pandas as pd
import datetime as dt

from numpy import ceil
from pydataxm.pydataxm import ReadDB

from model.Coleccion import Coleccion
from model.Consulta import Consulta
from model.Metrica import Metrica


class MercadoController:
    def __init__(self) -> None:
        super().__init__()
        self.coleccion_info_dic = {}
        self.consulta = Consulta()
        self.apiXML = ReadDB()

    def construir_info_metricas(self):
        url = f'http://servapibi.xm.com.co/lists'
        request = {'MetricId': "ListadoMetricas",
                    'Entity': "Sistema"}

        connection = requests.post(url, json=request)
        data_json = json.loads(connection.content)
        df_colecciones = pd.json_normalize(data_json['Items'], 'ListEntities', 'Date', sep='_')

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

    def agrupar_valores_resultados(self, input_df):

        if self.consulta.opc_agrup_result == "Dia":
            return self.agrupar_horas_dias(input_df)
        elif self.consulta.opc_agrup_result == "Ninguno":
            return input_df


    def consultar_metricas_XM(self):
        return self.apiXML.inventario_metricas

    def consultar_datos_XM(self, dias_consultados, max_dias_consulta):

        # Calcula la cantidad de llamadas que requiere la API
        cantidad_consultas_api = int(ceil(dias_consultados/max_dias_consulta))

        #Convierte el numero en un timedelta para usarlo en sumas
        max_dias_consulta =  dt.timedelta(days=int(max_dias_consulta))
        resultados_df = pd.DataFrame()
        print("Inicia la consulta")
        fecha_inicial_temp = self.consulta.fecha_inicial
        for i in range(cantidad_consultas_api):
            fecha_final_temp = fecha_inicial_temp + max_dias_consulta
            df_parcial = self.apiXML.request_data(
                coleccion=self.consulta.metrica_selecccionada.nombre_coleccion,
                metrica=self.consulta.metrica_selecccionada.metrica_idx,
                start_date=fecha_inicial_temp,
                end_date=fecha_final_temp)
            resultados_df = pd.concat([resultados_df, df_parcial])
            # Incrementa en uno para comenzar el siguiente rango y no repetir con el rango anterior
            # Avanza al siguiente rango de fechas
            fecha_inicial_temp = fecha_final_temp + dt.timedelta(days=1)
        return resultados_df
