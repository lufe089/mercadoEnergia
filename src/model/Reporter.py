import pandas as pd

import BaseConocimientoXM as bdXM
import datetime as dt

from src.util.Settings import ConsultasXMEnum, INPUT_DATA_PATH


class Reporter:

    def __init__(self):
        self.apiXM = bdXM.BaseConocimientoXM()
        self.consultas = [ConsultasXMEnum.DEMANDA_SIN_OPC, ConsultasXMEnum.DEMANDA_COMERCIAL_NO_REGULADA_OPC, ConsultasXMEnum.DEMANDA_COMERCIAL_REGULADA_OPC, ConsultasXMEnum.DEMANDA_TOTAL_AGENTES_OPC]

    def consultar_datos_historicos(self, consulta, anio_inicial, anio_final):

        limite_dias_api = dt.timedelta(days=29)
        df_todos_anios = pd.DataFrame()
        print("Inicia la consulta")
        for i in range(anio_inicial,anio_final+1,1):
            df_anual = pd.DataFrame()
            # Inicializa el dia_temp para que entre al ciclo
            primer_dia_anio = dt.date(i, 1, 1)
            dia_temp = primer_dia_anio
            anio = i
            is_cambiar_anio = False

            # Cuando la suma pase al siguiente anio termina el ciclo aunque se mantiene la ventana de consulta de la API
            while(is_cambiar_anio == False):
            #while(dia_temp.month <= 3): #solo para pruebas
                dia_temp = dia_temp + limite_dias_api

                # Al cambiar de anio se define manualmente el ultimo dia del anio aunque la consulta se haga por menos dias
                if (dia_temp.year > anio):
                    # ultimo dia del ano y termina la consulta para guardar todos los meses del anio en el mismo archivo pero solo hasta el 31
                    dia_temp = dt.date(anio, 12, 31)
                    is_cambiar_anio = True

                df_temp = self.apiXM.consultar_api(consulta, primer_dia_anio, dia_temp)
                df_anual = pd.concat([df_anual,df_temp])

                #Incrementa en uno para comenzar el siguiente rango y no repetir con el rango anterior
                #Avanza al siguiente rango de fechas
                primer_dia_anio = dia_temp + dt.timedelta(days=1)
            #Guarda los datos del anio
            file_name = INPUT_DATA_PATH + str(consulta.name)+str(i)+'.xlsx'
            #Index false evita que ponga el indice adiciona
            df_anual.to_excel(file_name,index = False)
            print("Datos guardados .... anio "+str(i))
            df_todos_anios = pd.concat([df_todos_anios,df_anual])

        # Exporta el archivo que tiene toda la info
        file_name = INPUT_DATA_PATH + str(consulta.name)  + str(anio_inicial) + '_' + str(anio_final) + '.xlsx'
        df_todos_anios.to_excel(file_name, index = False)
        print("Termino de analizar anios para consulta "+ str(consulta))

    def analizar_demanda_historica_agente(self, consulta, anio_inicial, anio_final ):

        # Leer el archivo del anio x
        # Agruparlo por proveedor
        # Agregar columna de anio
        # Agregar esto en un df temporal
        # Agregar el df temporal en un df consolidado
        # Guardar el df en un archivo de excel
        df_todos_anios = pd.DataFrame()
        print("Inicia el analisis demanda x anio")
        for i in range(anio_inicial, anio_final + 1, 1):
            df = IOData.leer_xlsx_to_df(INPUT_DATA_PATH+consulta.name+str(i)+'.xlsx')

            # Suma la demanda de energia de todo el año por agente
            df = df.groupby('Values_code')['Daily_Sum'].sum().to_frame()

            # Guardar el año para mantener la referencia
            df['Year'] = i
            df_todos_anios = pd.concat([df_todos_anios, df])

            """
            for key_group, group in df.groupby('Values_code'):
                grouped_agent = group['Daily_Sum'].sum()
                #"rouped_df['Values_code'] = key_group
                print('Agent: {} , Sum: {} \n'.format(key_group,grouped_agent))
            """

        # Exporta el archivo que tiene toda la info
        file_name = INPUT_DATA_PATH + str(consulta.name) + '_consol'+ str(anio_inicial) + '_' + str(anio_final) + '.xlsx'

        # El index es true pq el codigo del agente se vuelve el indice x el groupby
        df_todos_anios.to_excel(file_name, index=True)
        print("Termino de analizar anios para consulta " + str(consulta))

    def analizar_demanda_historica_SIN(self,anio_inicial, anio_final):
        df_todos_anios = pd.DataFrame()
        print("Inicia el analisis demanda x anio")
        for i in range(anio_inicial, anio_final + 1, 1):
            df = IOData.leer_xlsx_to_df(INPUT_DATA_PATH + ConsultasXMEnum.DEMANDA_SIN_OPC.name + str(i) + '.xlsx')

            # Agrupa por anio los valores, para lograr la agrupación por año se usa dt.year
            df = df.groupby(df['Date'].dt.year)['Value'].sum().to_frame()
            df_todos_anios = pd.concat([df_todos_anios, df])

        # Exporta el archivo que tiene toda la info
        file_name = INPUT_DATA_PATH + str(ConsultasXMEnum.DEMANDA_SIN_OPC.name) + '_consol' + str(anio_inicial) + '_' + str(
            anio_final) + '.xlsx'

        # El index es true pq el codigo del agente se vuelve el indice x el groupby
        df_todos_anios.to_excel(file_name, index=True)
        print("Termino de analizar consulta")

    def calcular_proporcion_agente(self, anio_inicial, anio_final):

        print("Inicia el analisis proporcion por agente")
        path_consolidado_SIN = INPUT_DATA_PATH + str(self.consultas[0].name) + '_consol' + str(
            anio_inicial) + '_' + str(
            anio_final) + '.xlsx'

        df_demanda_SIN = IOData.leer_xlsx_to_df(path_consolidado_SIN)
        # Inicia en 1 para no incluir la demana SIN
        # Datos demanda regulada, no regulada por comercializador y comercializador total
        for i in range(1, self.consultas.__len__()):

            # Arma la ruta donde se guarda la info
            path_consolidado_x_agente = INPUT_DATA_PATH + str(
                self.consultas[i].name) + '_consol' + str(anio_inicial) + '_' + str(
                anio_final) + '.xlsx'
            df_demanda_diaria_agente = IOData.leer_xlsx_to_df(path_consolidado_x_agente)

            # outer sirve para obtener todos los registros
            # guia aqui https://www.analyticslane.com/2018/09/10/unir-y-combinar-dataframes-con-pandas-en-python/
            #df_demanda_diaria_ana = pd.merge(df_demanda_SIN, df_demanda_diaria_agente, on='Date', how='outer')
            df_demanda_diaria_ana = pd.merge(df_demanda_SIN, df_demanda_diaria_agente, left_on='Date', right_on='Year', how='outer')

            # Renombra columna para facilitar analisis
            # guia aqui https://www.analyticslane.com/2021/11/08/pandas-renombrar-columnas-en-pandas/
            df_demanda_diaria_ana = df_demanda_diaria_ana.rename({'Value': 'Demand_By_Day_Tot'}, axis=1)
            df_demanda_diaria_ana['Perc_By_Agent'] = df_demanda_diaria_ana.apply(
                (lambda x: ((x['Daily_Sum'] * 100 / x['Demand_By_Day_Tot']))), 1)

            # Se elimina columna repetida con fechas . In place hace que los cambios se reflejen en el mismo dataset
            df_demanda_diaria_ana.drop(['Year'], axis = 1, inplace = True)

            # Eje 1 significa que se reciben las filas, llama a una función que se encarga de clasificar los agentes según la proporción que aporten
            df_demanda_diaria_ana["Tipo_Agente"] = df_demanda_diaria_ana.apply(self.clasificar_agente, axis=1)

            #Crea una variable categorica con los tipos de agentes
            df_demanda_diaria_ana["Tipo_Agente"] = df_demanda_diaria_ana["Tipo_Agente"].astype('category')

            # Cuenta cuantos veces a parece cada categoria en el dataframe
            df_demanda_diaria_ana["Tipo_Agente"].value_counts()

            # Crea variables dummy en el dataframe para cada tipo de agente
            #df_demanda_diaria_ana = pd.get_dummies(df_demanda_diaria_ana, columns=["Tipo_Agente"])
            #print(df_demanda_diaria_ana.dtypes)

            # Exporta el archivo que tiene toda la info
            file_name = INPUT_DATA_PATH + str(self.consultas[i].name) + '_proporcion' + str(
                anio_inicial) + '_' + str(
                anio_final) + '.xlsx'
            df_demanda_diaria_ana.to_excel(file_name, index=False)

            #df_demanda_agrupada_agente_anio = df_demanda_diaria_ana.groupby(['Values_code', 'Date', 'Tipo_Agente'])[
                #'Perc_By_Agent'].sum().to_frame()
            #df_demanda_agrupada_agente_anio = df_demanda_diaria_ana.groupby([  'Values_code','Tipo_Agente', 'Date'])[
            #'Perc_By_Agent'].sum().to_frame()

            df_demanda_agrupada_agente_anio = df_demanda_diaria_ana.groupby(['Date','Tipo_Agente', 'Values_code',])['Perc_By_Agent'].sum().to_frame()
            df_demanda_agrupada_agente_anio.to_excel(file_name + "fecha-tipo-codigo.xlsx", index=True)

            # Suma de la participacion de cada uno de los tipos de agentes por año
            # df_demanda_agrupada_agente_anio = df_demanda_diaria_ana.groupby(['Date'])['Values_code'].count().to_frame()
            df_participacion_tipo_agentes_anio = df_demanda_diaria_ana.groupby(['Date', 'Tipo_Agente'])[
                'Perc_By_Agent'].sum().to_frame()
            df_participacion_tipo_agentes_anio.to_excel(file_name + "participacion_tipo_agentes_anio.xlsx", index=True)


            # Cuantos agentes han habido por año
            df_cantidad_agentes_tipo_anio = df_demanda_diaria_ana.groupby(['Date','Tipo_Agente' ])[
            'Tipo_Agente'].count().to_frame()
            df_cantidad_agentes_tipo_anio.to_excel(file_name + "cont_date_tipoAgente.xlsx", index=True)

            print(df_demanda_agrupada_agente_anio)

            #return df_demanda_diaria_ana
        print("Termino de guardar los datos")

    def clasificar_agente(self,fila):
        # Suma las columnas de  las horas desde la hora 1 hasta la hora 24 aprovechando el indice que propone pandas
        if fila['Perc_By_Agent'] <= 0.01:
            return "NoRepresentativo"
        elif fila['Perc_By_Agent'] <=1:
            return "Pequenio"
        elif fila['Perc_By_Agent'] <=5:
            return "Mediano"
        elif fila['Perc_By_Agent'] >5:
            return "Grande"


    def consultar_datos_reporte_demanda(self, anio_inicial, anio_final):
        # Datos SIN, Datos demanda regulada, no regulada por comercializador y comercializador total
        for consulta in self.consultas:
            controller.consultar_datos_historicos(consulta, anio_inicial, anio_final)

    """
    Suma la demanda que ha tenido por agente, considerando las consultas por agente
    """
    def agrupar_demanda_historica(self, anio_inicial, anio_final):
        # Datos demanda regulada, no regulada por comercializador y comercializador total
        # Inicia en 1 para no incluir la demana SIN
        for i in range(1, self.consultas.__len__()):
            controller.analizar_demanda_historica_agente(self.consultas[i], anio_inicial, anio_final)


    def menu(self):
        print ("Opciones posibles:")
        print("Buscar en XM datos de demanda para un conjunto de anios:")
        print("Teniendo los datos en xlsx analizar demanda historica por anios por agente:")
        print("Teniendo los datos en xlsx analizar demanda historica del SIN:")
        opc = input("Escoge la opcion")
        if opc == 1:
            controller.consultar_datos_reporte_demanda(2014, 2021)
        elif opc == 2:
            controller.agrupar_demanda_historica(2014,2021)
        elif opc == 3:
            controller.analizar_demanda_historica_SIN(2014, 2021)


#ConsultasXMEnum.DEMANDA_SIN_OPC
controller = MercadoEnergiaController()
anio_inicial = 2014
anio_final = 2021
controller.calcular_proporcion_agente( anio_inicial, anio_final )