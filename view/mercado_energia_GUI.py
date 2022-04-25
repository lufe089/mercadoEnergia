import json
from datetime import timedelta, datetime

import numpy as np
import streamlit as st
from pydataxm import pydataxm
from streamlit_option_menu import option_menu
from pydataxm.pydataxm import ReadDB as apiXM, ReadDB
import pandas as pd


#from src.model.Reporter import Reporter
from controller.MercadoController import MercadoController

#from src.util.Settings import ConsultasXMEnum


class MercadoEnergiaGUI:

    def __init__(self) -> None:
        super().__init__()
        self.menu_actual = ""
        self.id_metrica_gui = ""
        self.agente_gui = ""
        self.fecha_inicial_gui = datetime.today() - timedelta(30)
        self.fecha_final_gui = datetime.today()
        self.tipo_metrica_gui = ""
        self.btn_buscar_gui = ""
        self._inicialializar_layout()

    def _inicialializar_layout(self):
        # Set page title, icon, layout wide (more used space in central area) and sidebar initial state
        st.set_page_config(page_title="Análisis mercado energía", page_icon='', layout="wide",
                           initial_sidebar_state="expanded")
        # Defines the number of available columns del area principal
        self.col1, self.col2, self.col3 = st.columns([1, 1, 1])

        # Define lo que abrá en la barra de menu
        with st.sidebar:
            self.menu_actual = option_menu("Menu", ["About", 'InfoMetrica','ConsultarAPI'],
                                           icons=['house', 'gear'], menu_icon="cast", default_index=1)

    def dibujar_consulta_api(self):
        # Lee el texto y elimina espacios en blanco - pasa a mínusculas
        self.id_metrica_gui = self.col1.text_input('Nombre métrica').lower().strip()

        self.agente_gui = self.col2.radio(
            "Agente asociado a la métrica",
            ('SISTEMA', 'AGENTE', 'RECURSO'))

        self.tipo_metrica_gui = self.col3.radio(
            "Tipo de métrica asociada",
            ('xHora', 'xDia', 'xMes'))

        self.fecha_inicial_gui = self.col2.date_input("Fecha inicial", self.fecha_inicial_gui)
        self.fecha_final_gui = self.col3.date_input("Fecha inicial", self.fecha_final_gui)

        self.btn_buscar_gui = st.button('Consultar')


    def print_welcome_text(self):
        return """
            #### 
            Este proyecto está hecho para facilitar el acceso y análisis de la información del **Mercado Energético Colombiano**.
    
            ####
            Las gráficas estan hechas con _Ploty_ y permiten: hacer zoom, ocultar trazos, descargar, etc.
    
            """

    def limpiar_opciones(self):
        #TODO verificar que esto no mate el programa
        #self.btn_buscar_gui = False
        #self.agrupar_x_dia_gui = False
        pass

    def convertir_df(self, df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    def test(self, metrica, agente, fecha_inicial, fecha_final):
        df_temp = apiXM.request_data(pydataxm.ReadDB(), metrica, agente, fecha_inicial, fecha_final)
        return df_temp


    def iniciar_GUI(self):
        self.controlerObj = MercadoController()
        # Filtro opciones de menu
        if self.menu_actual == "About":
            # Welcome message
            welcome = st.expander(label="Instrucciones", expanded=True)

            self.controlerObj.probar_hola()
            # Cuando este disponible en pantalla la instruccion de welcome
            with welcome:
                st.markdown(self.print_welcome_text())
                st.write("")
        elif self.menu_actual == "ConsultarAPI":
            self.dibujar_consulta_api()
            if self.btn_buscar_gui:
                st.write("Consultando ..")
                df_resultado = self.test(metrica=self.id_metrica_gui, agente=self.agente_gui, fecha_inicial=self.fecha_inicial_gui,
                fecha_final=self.fecha_final_gui)

                #df_resultado = self.reporterObj.test(metrica=self.id_metrica_gui, agente=self.agente_gui, fecha_inicial=self.fecha_inicial_gui,
                                 #fecha_final=self.fecha_final_gui)

                st.dataframe(data= df_resultado)

        elif self.menu_actual == "InfoMetrica":
            apiXML = ReadDB()
            self.data_metricas = apiXML.inventario_metricas
            coleccion_id = self.col1.selectbox("Consultar información métrica"
                'Metrica?',self.data_metricas.keys(), on_change=self.limpiar_opciones())
            st.table(data=self.data_metricas[coleccion_id])

            submetricas = []
            tipoMetrica = {}
            metricas_data = {}
            for metrica_data in self.data_metricas[coleccion_id]:
                    submetricas.append(metrica_data[1])
                    metricas_data[metrica_data[1]] = {"agente": metrica_data[2], "tipoMetrica":metrica_data[3], "parametro_llamada":metrica_data[0]}

            self.metrica_seleccionada_id = self.col2.radio(
                "Métrica",
                submetricas)

            self.col3.write(f"Tipo de métrica : {metricas_data[self.metrica_seleccionada_id]['tipoMetrica']}")
            self.fecha_inicial_gui = self.col1.date_input("Fecha inicial", self.fecha_inicial_gui)
            self.fecha_final_gui = self.col2.date_input("Fecha inicial", self.fecha_final_gui)

            # FIX cuando la metrica no tiene horario se muere, Cambiarlo a una solución objectual
            if metricas_data[self.metrica_seleccionada_id]["tipoMetrica"] == "Horaria":
                """En metricas horarias se transforman los valores a valores diarios"""
                self.agrupar_x_dia_gui = self.col3.checkbox("Agrupar x dia")

            self.btn_buscar_gui = st.button('Consultar')

            if self.btn_buscar_gui:
                resultados_df = apiXML.request_data(coleccion=coleccion_id, metrica= metricas_data[self.metrica_seleccionada_id]["parametro_llamada"], start_date= self.fecha_inicial_gui, end_date= self.fecha_final_gui)
                #df = apiXML.request_data(coleccion="AporEner", metrica= 1, start_date= self.fecha_inicial_gui, end_date= self.fecha_final_gui)

                #Si se selecciona el control de valores diarios
                if self.agrupar_x_dia_gui:
                    resultados_df = self.controlerObj.agrupar_horas_dias(resultados_df)
                st.dataframe(data=resultados_df)

                #nombre_archivo = f'large_df{str(self.fecha_inicial_gui)}-{str[self.fecha_final_gui]}.xlsx'
                csv_data = self.convertir_df(resultados_df)


                st.download_button(
                    label="Descargar data",
                    data=csv_data,
                    file_name="data-df.csv",
                    mime='text/csv',
                )
                #self.dibujar_consulta_api()
                #st.json(self.data_metricas)
                #st.write(self.metrica_seleccionada_id)


            #json_metrica= self.data_metricas[metrica_id]
            #json2=json.loads(json_metrica)

            #df_metrica_seleccionada = pd.DataFrame(json_metrica, orient="index")
            #st.dataframe(df_metrica_seleccionada)


# Main call
if __name__ == "__main__":
    gui = MercadoEnergiaGUI()
    gui.iniciar_GUI()
