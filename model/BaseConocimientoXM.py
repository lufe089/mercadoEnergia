# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Importar las librerias y configurar visualizacion
from pydataxm import *                           #Se realiza la importación de las librerias necesarias para ejecutar
import datetime as dt
from pydataxm.pydataxm import ReadDB as apiXM    #Se importa la clase que invoca el servicio
import pandas as pd

# Configuracion de tres decimales en visualizacion
from util.Settings import ConsultasXMEnum

pd.options.display.float_format  = '{:,.3f}'.format

"""
Info de la API
https://github.com/EquipoAnaliticaXM/API_XM
"""
# Constantes generales de la API
METRICA_SISTEMA = 0
METRICA_AGENTE = 1
DEMANDA_COMERCIAL_REGULADA = "DemaComeReg"
DEMANDA_COMERCIAL_NO_REGULADA = "DemaComeNoReg"
DEMANDA_COMERCIAL_TOTAL = "DemaCome"
DEMANDA_SIN = "DemaSIN"
LISTADO_METRICAS = "ListadoMetricas"
LISTADO_AGENTES = "ListadoAgentes"


class BaseConocimientoXM:

    def __init__(self):

        df_to_save = pd.DataFrame()

    def consultar_api(self, consulta, fecha_inicio = None, fecha_fin = None):
        df = pd.DataFrame()
        if consulta == ConsultasXMEnum.DEMANDA_COMERCIAL_REGULADA_OPC:
            df = self.consultar_demanda_horaria_agrupada_diaria_agente(fecha_inicio, fecha_fin, DEMANDA_COMERCIAL_REGULADA )
        elif consulta == ConsultasXMEnum.DEMANDA_COMERCIAL_NO_REGULADA_OPC:
            df = self.consultar_demanda_horaria_agrupada_diaria_agente(fecha_inicio, fecha_fin,
                                                                      DEMANDA_COMERCIAL_NO_REGULADA)
        elif consulta == ConsultasXMEnum.DEMANDA_TOTAL_AGENTES_OPC:
            df = self.consultar_demanda_horaria_agrupada_diaria_agente(fecha_inicio, fecha_fin,
                                                                      DEMANDA_COMERCIAL_TOTAL)
        elif consulta == ConsultasXMEnum.DEMANDA_SIN_OPC:
            df = self.consultar_demanda_diaria_sistema(fecha_inicio, fecha_fin,
                                                                       DEMANDA_SIN)
        elif consulta == ConsultasXMEnum.LISTADO_METRICAS_OPC:
            df = self.consultar_listas(LISTADO_METRICAS)
        elif consulta == ConsultasXMEnum.LISTADO_AGENTES_OPC:
            df = self.consultar_listas(LISTADO_AGENTES)
        return df

    def consultar_listas(self,consulta):
        # Fechas dummy el servicio realmente no las necesita
        fecha_inicio = dt.date(2021, 1, 1)
        fecha_fin = dt.date(2021, 1, 10)
        df = apiXM.request_data(pydataxm.ReadDB(), consulta, METRICA_SISTEMA,fecha_inicio, fecha_fin)
        return df


    def sumar_metrica_horaria_to_diaria(self, fila):
        suma = 0.0
        # Suma las columnas de  las horas desde la hora 1 hasta la hora 24 aprovechando el indice que propone pandas
        for i in range(2, 26):
            suma = suma + fila[i]

        return suma

    def consultar_demanda_horaria_agrupada_diaria_agente(self, fecha_inicio, fecha_fin, metricId):
        df = apiXM.request_data(pydataxm.ReadDB(),  # Se indica el objeto que contiene el serivicio
                                metricId, METRICA_AGENTE, fecha_inicio,  # Corresponde a la fecha inicial de la consulta
                                fecha_fin)
        # Limpiar datos para quitar NaN
        df = df.fillna(value=0)

        # Eje 1 significa que se reciben las filas
        df["Daily_Sum"] = df.apply(self.sumar_metrica_horaria_to_diaria, axis=1)

        # Guardar el resumen de los datos diarios
        # Values_code tiene el codigo del agente
        df = df[['Values_code', 'Date', 'Daily_Sum']]
        return df

    """
    Consultas que sean diarias, necesiten metrica SISTEMA
    """
    def consultar_demanda_diaria_sistema(self,fecha_inicio, fecha_fin, tipo_demanda):
        df_demanda_SIN = apiXM.request_data(pydataxm.ReadDB(),  # Se indica el objeto que contiene el serivicio
                                            tipo_demanda, METRICA_SISTEMA, fecha_inicio,
                                            # Corresponde a la fecha inicial de la consulta
                                            fecha_fin)
        return df_demanda_SIN

