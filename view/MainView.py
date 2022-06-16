import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pydataxm.pydataxm import ReadDB
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
            self.consulta = Consulta()
            self.apiXML = ReadDB()
            self.btn_buscar_gui = False
            self.controller = MercadoController()

            # Consulta información de todas las metricas
            self.controller.construir_info_metricas()

            st.session_state['main_view'] = self
        else:
            self.menu_actual = st.session_state.main_view.menu_actual
            self.controller = st.session_state.main_view.controller
            self.consulta = st.session_state.main_view.consulta
            self.apiXML = st.session_state.main_view.apiXML
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
        self.consulta.is_agrupar_x_dia_gui = False

    def convertir_df(self, df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    def _dibujar_lista_metricas(self):
        self.data_metricas = self.apiXML.inventario_metricas
        self.consulta.coleccion_id = self.col1.selectbox("Consultar información métrica"
                                                         'Metrica?', self.data_metricas.keys(),
                                                         on_change=self.limpiar_opciones())

        # st.table(data=self.data_metricas[coleccion_id])

        submetricas = []
        idx_metrica = 0
        for metrica_data in self.data_metricas[self.consulta.coleccion_id]:
            metrica_temp = Metrica(nombre_metrica=metrica_data[1], tipo_metrica=metrica_data[3],
                                   parametro_llamada=metrica_data[0], entidad=metrica_data[2],
                                   nombre_coleccion=self.consulta.coleccion_id, metrica_idx=idx_metrica)
            self.consulta.metricas[metrica_temp.nombre_metrica] = metrica_temp
            submetricas.append(metrica_data[1])
            idx_metrica += 1
            # elf.metricas_list_data[metrica_data[1]] = {"agente": metrica_data[2], "tipoMetrica": metrica_data[3],
            # "parametro_llamada": metrica_data[0]}

        self.consulta.metrica_seleccionada_id = self.col2.radio(
            "Métrica",
            submetricas)
        self.consulta.metrica_selecccionada = self.consulta.metricas[self.consulta.metrica_seleccionada_id]

    def dibujar_info_coleccion(self, nombre_coleccion):
        """Dibuja informacion de la colección como la descripcion de loq ue consulta, la cantidad maxima de dias de consulta
         y la unidad de medida de los resultados"""
        if self.controller.coleccion_info_dic.get(nombre_coleccion):
            datos_coleccion = self.controller.coleccion_info_dic.get(nombre_coleccion)

            # Al sobreescribir el metodo str entonces aqui se imprimen directamente los valores con el formato que sea interesante para losd
            # datos
            st.info(datos_coleccion)

    def dibujar_grafico_resumen(self, df, nombre_metrica, nombre_coleccion, fecha_inicial, fecha_final, entidad):

        # Validar si existe el campu value de tipo numerico y el campo fecha para hacer el grafico resumen, por ahora estos graficos son solamente para consultas de sistema
        if entidad == "Sistema" and 'Value' in df.columns and 'Date' in df.columns:
            chart_data = df[['Date', 'Value']]
            if self.controller.coleccion_info_dic.get(nombre_coleccion):

                # INFO sobre la libreria https://plotly.com/python/line-charts/
                datos_coleccion = self.controller.coleccion_info_dic.get(nombre_coleccion)
                fig = go.Figure()

                fig.add_trace(go.Scatter(x=chart_data['Date'], y=chart_data['Value'],
                                         mode='lines+markers', name='markers'))

                annotations = []

                #Ajustes respecto al titulo
                annotations.append(dict(xref='paper', yref='paper', x=0.5, y=1.05,
                                        xanchor='center', yanchor='bottom',
                                        text=f"Resumen {nombre_metrica}: [{fecha_inicial}- {fecha_final}]",
                                        font=dict(family='Arial',
                                                  size=25,
                                                  color='rgb(37,37,37)'),
                                        showarrow=False))

                fig.update_layout(xaxis_title='Mes',
                                  yaxis_title=f'{nombre_metrica}({datos_coleccion.unidades_metrica})', annotations=annotations)

                #fig = px.line(df, x="Date", y="Value", markers=True, xaxis_title='Mes',
                              #title=f"{nombre_metrica} [{fecha_inicial}- {fecha_final}]",
                              #yaxis_title=f'{nombre_metrica}({datos_coleccion.unidades_metrica})')
                st.plotly_chart(fig, use_container_width=True)

    def dibujar_consulta_metricas(self):

        # Dibujar checkbox
        self._dibujar_lista_metricas()
        errores = False
        resultados_df = None

        self.col3.write(f"Tipo de métrica : {self.consulta.metrica_selecccionada.tipo_metrica}")
        self.consulta.fecha_inicial = self.col1.date_input("Fecha inicial", self.consulta.fecha_inicial)
        self.consulta.fecha_final = self.col2.date_input("Fecha inicial", self.consulta.fecha_final)

        if self.consulta.es_consulta_horaria() and (self.consulta.fecha_final - self.consulta.fecha_inicial).days >= 30:
            st.error("La consulta de métricas con valor Horario es máximo 30 días, reduzca el rango de la consulta")
            errores = True
        else:
            errores = False

        if not errores:
            if self.consulta.es_consulta_horaria():
                """En metricas horarias se transforman los valores a valores diarios"""
                self.consulta.is_agrupar_x_dia_gui = self.col3.checkbox(label="Agrupar x dia", value=True)
            else:
                self.consulta.is_agrupar_x_dia_gui = False

            self.btn_buscar_gui = st.button('Consultar')
            datos_encontrados = False
            progreso_barra = None

            if self.btn_buscar_gui:
                # Muestra detalles sobre la coleccion como la info que consulta y los valores de resultado
                self.dibujar_info_coleccion(self.consulta.metrica_selecccionada.nombre_coleccion)

                if not datos_encontrados:
                    progreso_barra = st.progress(0)

                    resultados_df = self.apiXML.request_data(
                        coleccion=self.consulta.metrica_selecccionada.nombre_coleccion,
                        metrica=self.consulta.metrica_selecccionada.metrica_idx,
                        start_date=self.consulta.fecha_inicial,
                        end_date=self.consulta.fecha_final)
                    # Verifica que hayan resultados disponibles
                    if resultados_df.empty:
                        mensaje = "No hay datos disponibles en la consulta"
                        st.warning(mensaje)
                    else:
                        datos_encontrados = True
                if datos_encontrados:
                    progreso_barra.progress(100)
                    # Si se selecciona el control de valores diarios
                    if self.consulta.is_agrupar_x_dia_gui:
                        try:
                            resultados_df = self.controller.agrupar_horas_dias(resultados_df)
                        except ValueError as ex:
                            # Muestra el mensaje en pantalla
                            st.error(str(ex))

                    # Grafica el resultado
                    self.dibujar_grafico_resumen(resultados_df,
                                                 nombre_metrica=self.consulta.metrica_selecccionada.nombre_metrica,
                                                 nombre_coleccion=self.consulta.metrica_selecccionada.nombre_coleccion,
                                                 fecha_inicial=self.consulta.fecha_inicial,
                                                 fecha_final=self.consulta.fecha_final, entidad = self.consulta.metrica_selecccionada.entidad )

                    # Muestra los datos en tablas
                    st.subheader('Detalles')
                    st.dataframe(data=resultados_df)
                    csv_data = self.convertir_df(resultados_df)
                    # resultados_df = resultados_df[['Daily_Sum']]
                    # st.line_chart(resultados_df)
                    fecha_inicial_string = self.consulta.fecha_inicial.strftime('%d/%m/%Y')
                    fecha_final_string = self.consulta.fecha_final.strftime('%d/%m/%Y')
                    fechas = fecha_final_string + '-' + fecha_inicial_string
                    nombre_archivo = f'{self.consulta.metrica_seleccionada_id}{fechas}.csv'
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
