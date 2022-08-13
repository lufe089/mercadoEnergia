import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

from controller.MercadoController import MercadoController
from model.Consulta import Consulta
from model.Metrica import Metrica
from view.AboutPartial import *


class MainView:

    def __init__(self) -> None:
        super().__init__()

        if 'main_view' not in st.session_state:
            self.menu_actual = "About"
            self.btn_buscar_gui = False
            self.controller = MercadoController()

            # Consulta información de todas las metricas
            self.controller.construir_info_metricas()

            st.session_state['main_view'] = self
        else:
            self.menu_actual = st.session_state.main_view.menu_actual
            self.controller = st.session_state.main_view.controller
            self.btn_buscar_gui = False
        self._inicialializar_layout()

    def _inicialializar_layout(self):
        # Set page title, icon, layout wide (more used space in central area) and sidebar initial state
        st.set_page_config(page_title="Análisis mercado energía", page_icon='', layout="wide",
                           initial_sidebar_state="expanded")
        # Defines the number of available columns del area principal
        self.col1, self.col2, self.col3 = st.columns([1, 1, 1])

        # Define lo que abrá en la barra de menu
        with st.sidebar:
            self.menu_actual = option_menu("Menu", ["About", '[Métricas]Consultas sencillas'],
                                           icons=['house', 'gear'], menu_icon="cast", default_index=1)

    def limpiar_opciones(self):
        # TODO verificar que esto no mate el programa
        self.controller.consulta.is_agrupar_x_dia_gui = False

    def convertir_df(self, df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        # Muy importante que tengamos el separador como , por lo mismo
        return df.to_csv(encoding = 'utf-8', decimal=',')

    def _dibujar_lista_metricas(self):
        self.data_metricas = self.controller.consultar_metricas_XM()
        self.controller.consulta.coleccion_id = self.col1.selectbox("Consultar información métrica"
                                                         'Metrica?', self.data_metricas.keys(),
                                                         on_change=self.limpiar_opciones())

        # st.table(data=self.data_metricas[coleccion_id])

        submetricas = []
        idx_metrica = 0
        for metrica_data in self.data_metricas[self.controller.consulta.coleccion_id]:
            metrica_temp = Metrica(nombre_metrica=metrica_data[1], tipo_metrica=metrica_data[3],
                                   parametro_llamada=metrica_data[0], entidad=metrica_data[2],
                                   nombre_coleccion=self.controller.consulta.coleccion_id, metrica_idx=idx_metrica)
            self.controller.consulta.metricas[metrica_temp.nombre_metrica] = metrica_temp
            submetricas.append(metrica_data[1])
            idx_metrica += 1
            # elf.metricas_list_data[metrica_data[1]] = {"agente": metrica_data[2], "tipoMetrica": metrica_data[3],
            # "parametro_llamada": metrica_data[0]}

        self.controller.consulta.metrica_seleccionada_id = self.col2.radio(
            "Métrica",
            submetricas)
        self.controller.consulta.metrica_selecccionada = self.controller.consulta.metricas[self.controller.consulta.metrica_seleccionada_id]

    def dibujar_info_coleccion(self, nombre_coleccion):
        """Dibuja informacion de la colección como la descripcion de loq ue consulta, la cantidad maxima de dias de consulta
         y la unidad de medida de los resultados"""
        if self.controller.coleccion_info_dic.get(nombre_coleccion):
            datos_coleccion = self.controller.coleccion_info_dic.get(nombre_coleccion)
            # Al sobreescribir el metodo str entonces aqui se imprimen directamente los valores con el formato que sea interesante para losd
            # datos
            st.info(datos_coleccion)

    def dibujar_grafico_resumen(self, df, nombre_metrica, nombre_coleccion, fecha_inicial, fecha_final, entidad):
        # Validar si existe el campu value de tipo numerico y el campo fecha para hacer el grafico resumen
        if 'Value' in df.columns and 'Date' in df.columns:
            chart_data_df = pd.DataFrame()
            if 'Name' in df.columns:
                  #chart_data_df.loc[:,'Name'] = df.loc[:,'Name']
                  chart_data_df['Name'] = df['Name']
            chart_data_df['Date'] =  df['Date']
            chart_data_df['Value'] = df['Value']

            # se buscan  datos de la metrica en la coleccion como la unidad de medida y el nombre de la colección
            if self.controller.coleccion_info_dic.get(nombre_coleccion):

                # INFO sobre la libreria https://plotly.com/python/line-charts/
                datos_coleccion = self.controller.coleccion_info_dic.get(nombre_coleccion)
                layout = go.Layout(separators=", ")
                fig = go.Figure(layout = layout)

                if 'Name' in chart_data_df.columns:

                    # Consulta los nombres de las posibles series y luego para cada uno agrega la serie al gráfico
                    nombres_series_grafico = chart_data_df['Name'].unique()
                    for nombre in nombres_series_grafico:
                        serie_grafico_df = chart_data_df.query("Name == @nombre")
                        fig.add_trace(go.Scatter(x=serie_grafico_df['Date'], y=serie_grafico_df['Value'], name = nombre,
                                                 mode='lines+markers'))
                else:
                    # Agrega una unica serie al grafico que tendra los valores agrupados
                    fig.add_trace(go.Scatter(x=chart_data_df['Date'], y=chart_data_df['Value'],
                                         mode='lines+markers',line= dict(dash='dashdot')) )
                annotations = []
                #Ajustes respecto al titulo
                annotations.append(dict(xref='paper', yref='paper', x=0.5, y=1.05,
                                        xanchor='center', yanchor='bottom',
                                        text=f"Resumen {nombre_metrica}: [{fecha_inicial} / {fecha_final}]",
                                        font=dict(family='Arial',
                                                  size=25,
                                                  color='rgb(37,37,37)'),
                                        showarrow=False))
                # Sobre leyendas
                #https://plotly.com/python/legend/

                # Sobre shapes
                #https://plotly.com/python/shapes/

                # Configura el grafico. Detalles aqui: https://plotly.com/python/configuration-options/#removing-modebar-buttons
                fig.update_layout(xaxis_title='Fecha',
                                  yaxis_title=f'{nombre_metrica}({datos_coleccion.unidades_metrica})', annotations=annotations,
                                  newshape=dict(line_color='red', line_width=1),
                                  modebar_add=['drawline',
                                               'drawcircle',
                                               'drawrect',
                                               'eraseshape'
                                               ],
                                  )

                #fig = px.line(df, x="Date", y="Value", markers=True, xaxis_title='Mes',
                              #title=f"{nombre_metrica} [{fecha_inicial}- {fecha_final}]",
                              #yaxis_title=f'{nombre_metrica}({datos_coleccion.unidades_metrica})')
                st.plotly_chart(fig, use_container_width=True)

    def __ajustar_decimales_y_miles(self,value):
        value = round(value, 2)

        # Esta parte se comenta porque al convertirlo se vuelve cadena, y entonces ya no permite hacer el orde

        #value = "{:,}".format(value).replace(',', '~').replace('.', ',').replace('~', '')
        #formated_value= float(formated_value)
        return value


    def ajustar_dataframe_resultado(self,df):

        """ Cuando la entidad no es sistema los datos estan agrupados en algunas consultas por la columna Values_code y en otra por la columna Name
         en esta condición se unifica el nombre de la columna para facilitar la elaboración del gráfico
         """
        if 'Values_code' in df.columns:
            # chart_data.loc[:,'Name'] = df.loc[:,'Values_code']
            df.rename(columns={'Values_code': 'Name'}, inplace=True)


        if 'Code' in df.columns:
            # chart_data.loc[:,'Name'] = df.loc[:,'Values_code']
            df.rename(columns={'Code': 'Name'}, inplace=True)

        # Si el resultado tiene un campo para los valores, hace los ajustes para que vuelva las , puntos y viceversa
        if 'Value' in df.columns:
            df['Value'] = df['Value'].apply(lambda x: self.__ajustar_decimales_y_miles(x))
            s = df.style.format({"Value": lambda x: '{:,.1f}'.format(x)})
        return df

    def dibujar_opc_agrupar(self, es_mas_de_un_mes):
        opciones = []
        #if es_mas_de_un_mes:
           # opciones.append("Mes")
        if  self.controller.consulta.es_consulta_horaria():
            """En metricas horarias se transforman los valores a valores diarios"""
            opciones.append("Dia")
        opciones.append("Ninguno")
        self.controller.consulta.opc_agrup_result = self.col3.radio("Agrupar por:",opciones)


    def dibujar_consulta_metricas(self):

        # Dibujar checkbox
        self._dibujar_lista_metricas()
        resultados_df = None

        self.col3.write(f"Tipo de métrica : {self.controller.consulta.metrica_selecccionada.tipo_metrica}")
        self.controller.consulta.fecha_inicial = self.col1.date_input("Fecha inicial", self.controller.consulta.fecha_inicial)
        self.controller.consulta.fecha_final = self.col2.date_input("Fecha inicial", self.controller.consulta.fecha_final)

        dias_consultados = (self.controller.consulta.fecha_final - self.controller.consulta.fecha_inicial).days
        max_dias_consulta = self.controller.coleccion_info_dic.get(self.controller.consulta.coleccion_id).max_dias

        es_mas_de_un_mes = dias_consultados > max_dias_consulta

        # Dibuja las opciones para agrupar los datos
        self.dibujar_opc_agrupar(es_mas_de_un_mes)

        self.btn_buscar_gui = st.button('Consultar')
        datos_encontrados = False

        if self.btn_buscar_gui:
            # Valida los tiempos maximos de consulta y notifica
            if dias_consultados > max_dias_consulta:
                mensaje_respuesta = f"La consulta excede el máximo de {max_dias_consulta} días que permite XM. Tomará un poco más de tiempo su construcción"
                st.warning(mensaje_respuesta)

            # Muestra detalles sobre la coleccion como la info que consulta y los valores de resultado
            progreso_barra = st.progress(20)
            self.dibujar_info_coleccion(self.controller.consulta.metrica_selecccionada.nombre_coleccion)

            if not datos_encontrados:
                st.spinner(text="Consultando la información...")
                resultados_df = self.controller.consultar_datos_XM(dias_consultados=dias_consultados, max_dias_consulta=max_dias_consulta)
                # Verifica que hayan resultados disponibles
                if resultados_df.empty:
                    mensaje = "No hay datos disponibles en la consulta"
                    progreso_barra = st.progress(100)
                    st.warning(mensaje)

                else:
                    datos_encontrados = True
            if datos_encontrados:
                progreso_barra.progress(50)
                # Agrupa los resultados cuando aplica
                try:
                    st.spinner(text="Agrupando los resultados...")
                    resultados_df = self.controller.agrupar_valores_resultados(resultados_df)
                    progreso_barra.progress(60)
                except ValueError as ex:
                    # Muestra el mensaje en pantalla
                    st.error(str(ex))

                # Ajusta columnas para facilitar el dibujo de las graficas
                resultados_df = self.ajustar_dataframe_resultado(resultados_df)
                progreso_barra.progress(70)
                # Grafica el resultado
                try:
                    st.spinner(text="Dibujando gráfico de resultados...")
                    self.dibujar_grafico_resumen(resultados_df,
                                                 nombre_metrica=self.controller.consulta.metrica_selecccionada.nombre_metrica,
                                                 nombre_coleccion=self.controller.consulta.metrica_selecccionada.nombre_coleccion,
                                                 fecha_inicial=self.controller.consulta.fecha_inicial,
                                                 fecha_final=self.controller.consulta.fecha_final, entidad = self.controller.consulta.metrica_selecccionada.entidad )

                except ValueError as ex:
                    # Muestra el mensaje en pantalla
                    st.error("Los datos recibidos no permiten dibujar gráfico resumen")
                    print((ex.__str__()))
                finally:
                    progreso_barra.progress(100)
                # Muestra los datos en tablas
                st.subheader('Detalles')
                st.dataframe(data=resultados_df)
                csv_data = self.convertir_df(resultados_df)
                fecha_inicial_string = self.controller.consulta.fecha_inicial.strftime('%d/%m/%Y')
                fecha_final_string = self.controller.consulta.fecha_final.strftime('%d/%m/%Y')
                fechas = fecha_final_string + '-' + fecha_inicial_string
                nombre_archivo = f'{self.controller.consulta.metrica_seleccionada_id}{fechas}.csv'
                st.download_button(
                    label="Descargar data",
                    data=csv_data,
                    file_name=nombre_archivo,
                    mime='text/csv',
                )

    def controlar_menu(self):
        # Filtro opciones de menu
        if self.menu_actual == "About":
            # Welcome message
            welcome = st.expander(label="Instrucciones", expanded=True)

            # Cuando este disponible en pantalla la instruccion de welcome
            with welcome:
                st.markdown(mostrar())
                st.write("")
        elif self.menu_actual == "[Métricas]Consultas sencillas":
            self.dibujar_consulta_metricas()


# Main call
if __name__ == "__main__":
    gui = MainView()
    gui.controlar_menu()
