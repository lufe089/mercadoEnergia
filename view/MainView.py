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
        pass

    def convertir_df(self, df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')
        # return df.to_excel(r'prueba.xlsx')

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
            # elf.metricas_list_data[metrica_data[1]] = {"agente": metrica_data[2], "tipoMetrica": metrica_data[3],
            # "parametro_llamada": metrica_data[0]}

        self.consulta.metrica_seleccionada_id = self.col2.radio(
            "Métrica",
            submetricas)
        self.consulta.metrica_selecccionada = self.consulta.metricas[self.consulta.metrica_seleccionada_id]

    def dibujar_consulta_metricas(self):

        # Dibujar checkbox
        self._dibujar_lista_metricas()
        self.mensaje = ""
        errores = False

        self.col3.write(f"Tipo de métrica : {self.consulta.metrica_selecccionada.tipo_metrica}")
        self.consulta.fecha_inicial = self.col1.date_input("Fecha inicial", self.consulta.fecha_inicial)
        self.consulta.fecha_final = self.col2.date_input("Fecha inicial", self.consulta.fecha_final)

        if self.consulta.es_consulta_horaria() and (self.consulta.fecha_final-self.consulta.fecha_inicial).days >= 30:
            st.error("La consulta de métricas con valor Horario solo puede ser de 30 días")
            errores = True
        else:
            errores = False

        if self.consulta.es_consulta_horaria():
            """En metricas horarias se transforman los valores a valores diarios"""
            self.consulta.is_agrupar_x_dia_gui = self.col3.checkbox("Agrupar x dia")
        else:
            self.consulta.is_agrupar_x_dia_gui = False

        self.btn_buscar_gui = st.button('Consultar')
        datos_encontrados = False
        progreso_barra = None

        if self.btn_buscar_gui:
            if not datos_encontrados:
                progreso_barra = st.progress(0)

                resultados_df = self.apiXML.request_data(coleccion=self.consulta.metrica_selecccionada.nombre_coleccion,
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
                    resultados_df = self.controller.agrupar_horas_dias(resultados_df)
                st.dataframe(data=resultados_df)
                # nombre_archivo = f'large_df{str(self.fecha_inicial_gui)}-{str[self.fecha_final_gui]}.xlsx'
                csv_data = self.convertir_df(resultados_df)
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

    def iniciar_GUI(self):
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
    gui.iniciar_GUI()