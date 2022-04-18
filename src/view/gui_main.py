import time
from datetime import date, timedelta, datetime

import streamlit as st
from streamlit_option_menu import option_menu

example_options = {
     "Precios":{
        "max_date":date.today()+timedelta(days=1), # Max date in date selector
        "min_date":datetime(2014, 1, 1), # Min date in date selector
        "start_date":date.today()-timedelta(days=30), # Initial date selected
        "end_date":date.today()-timedelta(days=15), # final date initially selected
        "markets":["MDA","MTR"], # Markets checkboxes options
        "mean_or_sum":"mean", # MWh == sum, $/MWh == mean
        "component":{
            "options":["Precio de Energía [$/MWh]","Componente de Energía [$/MWh]", "Componente de Pérdidas [$/MWh]","Componente de Congestión [$/MWh]"], # Component dropdown options
            "title":"Componente de Precios:", # Component dropdown title
            "help":"Componente de precios a graficar."  # Component dropdown help
        },
        "plot_options":{
            "title":"Valores a graficar:", # Plot_options dropdown title
            "help":"Grafica el valor promedio por hora, día, semana, promedio de cada hora por día de la semana o promedio de cada hora por mes." # Plot_options dropdown help
        }
    },
    "Cantidades Asignadas":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2017, 1, 1),
        "start_date":date.today()-timedelta(days=30), # Initial date selected
        "end_date":date.today()-timedelta(days=15), # final date initially selected
        "markets":["MDA"],
        "mean_or_sum":"sum",
        "component":{
            "options":["Energía Total Asignada [MWh]","Energía Asignada a Cargas Directamente Modeladas [MWh]","Energía Asignada a Cargas Indirectamente Modeladas [MWh]"],
            "title":"Tipo de carga a graficar:",
            "help":"Cargas directamente modeladas, indirectamente modeladas o ambas (suma)"
        },
        "plot_options":{
            "title":"Valores a graficar:",
            "help":"Grafica el valor total (suma) por hora, día, semana, promedio de cada hora por día de la semana o promedio de cada hora por mes."
        }
    },
    "Demanda":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2018, 1, 1),
        "start_date":date.today()-timedelta(days=180), # Initial date selected
        "end_date":date.today()-timedelta(days=165), # final date initially selected
        "markets":["MDA","MDA-AUGC","MTR"],
        "mean_or_sum":"sum",
        "component":{
            "options":["Demanda de Energía [MWh]"],
            "title":"Valor a graficar:",
            "help":"Energía total"
        },
        "plot_options":{
            "title":"Valores a graficar",
            "help":"Grafica el valor total (suma) por hora, día, semana, promedio de cada hora por día de la semana o promedio de cada hora por mes."
        }
    },
    "Generación":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2018, 1, 1),
        "start_date":date.today()-timedelta(days=180), # Initial date selected
        "end_date":date.today()-timedelta(days=165), # final date initially selected
        "markets":["MDA-Intermitentes","MTR-SEN"],
        "mean_or_sum":"sum",
        "component":{
            "options":["Generación de Energía [MWh]"],
            "title":"Valor a graficar:",
            "help":"Generación de energía por tipo de tecnología"
        },
        "plot_options":{
            "title":"Valores a graficar",
            "help":"Grafica el valor total (suma) por hora, día, semana, promedio de cada hora por día de la semana o promedio de cada hora por mes."
        },
        "second_plot_options":{
            "title":"Valores a graficar:",
            "help":"Grafica el valor total (suma) por hora, día, semana, promedio de cada hora por día de la semana o promedio de cada hora por mes.",
            "options":["Horario","Diario", "Semanal","Promedio Horario por Día de la Semana", "Promedio Horario por Mes"]
        }
    }
}

analysis_options = {
"Demanda":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2014, 1, 1),
        "start_date":date.today(), # Initial date selected
        "end_date":date.today()-timedelta(days=365), # final date initially selected
        "markets":["Regulado", "No regulado"],
        "demand_types":["Histórico SIN", "Agente"]
},
"ConsultarMetricas":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2014, 1, 1),
        "start_date":date.today()-timedelta(days=180), # Son datos dummy
        "end_date":date.today()-timedelta(days=165), # son datos dummy
        "markets":[],
        "demand_types":[]
},
"Metricas":{
        "max_date":date.today()+timedelta(days=1),
        "min_date":datetime(2014, 1, 1),
        "start_date":date.today()-timedelta(days=180), # Initial date selected
        "end_date":date.today()-timedelta(days=165), # final date initially selected
        "markets":["Regulado", "No regulado"],
        "demand_types":[]
}
}

## Verificacion de datos
def check_dates(dates):
    """Checks if dates are selected"""
    if len(dates)!=2:
        st.stop()

def check_multi_options(options):
    """Checks if there is at least an option of a multi-option field selected"""
    if not any(options):
        st.sidebar.warning('Selecciona una opción.')
        st.stop()


def pack_dates(start_date, end_date, market="", limit_dates=True):
    """Gets days to ask for info and start date, returns appropiate data intervals to assemble APIs url"""

    # For open source APIs date interval for resquest is bigger
    date_interval = 200 if not limit_dates else 7

    # To avoid CENACE error in MTR API last date of MTR API call is limited
    if market == 'MTR' and end_date > date.today() - timedelta(days=7):
        end_date = date.today() - timedelta(days=7)

    dates = []
    delta = end_date - start_date
    days = delta.days

    # Pack dates every 'date_interval' days.
    while days >= 0:

        if days >= date_interval:
            last_date = start_date + timedelta(days=date_interval - 1)
            dates.append([str(start_date), str(last_date)])
            start_date = last_date + timedelta(days=1)
            days -= date_interval

        else:
            last_date = end_date
            dates.append([str(start_date), str(last_date)])
            days = -1

    return dates

def draw_sidebar():
    add_selectbox = st.sidebar.selectbox(
        "Demanda",
        ("Demanda SIN", "DemandaCom Reg", "DemandaCom NOREG")
    )


def print_welcome_text():
    return """
        #### ¡Hola!
        Este proyecto está hecho para facilitar el acceso y análisis de la información del **Mercado Energético Colombiano**.
        
        La parte gráfica del proyecto está inspirada en el trabajo de [Angel Carballo](https://share.streamlit.io/angelcarballocremades/energy-price-dashboard/app.py)
        
        Básicamente debes: 

        1. **Elegir** las opciones deseadas de la **barra lateral**.
        2. **Esperar** a que la información se descargue y la gráfica aparezca (**Si no la ves, desplázate hacia abajo**).
        3. **Seleccionar** el tipo de **visualización** deseada.
        ####
        Las gráficas estan hechas con _Ploty_ y permiten: hacer zoom, ocultar trazos, descargar, etc.

        """

def main():
    # Set page title, icon, layout wide (more used space in central area) and sidebar initial state
    st.set_page_config(page_title="Análisis mercado energía", page_icon='', layout="wide",
                       initial_sidebar_state="expanded")

    # Central area header
    # Defines the number of available columns
    col1, col2, = st.columns([1, 9])

    col2.write("# Mercado de energía en Colombia")
    col2.markdown("Inspirado en proyecto de [Ángel Carballo](https://github.com/AngelCarballoCremades/Energy-Price-Dashboard/)")

    # Welcome message
    welcome = st.expander(label="Bienvenida", expanded=True)
    with welcome:
        st.markdown(print_welcome_text())
        st.write("")

    """
    # Instructions message
    instructions = st.expander(label="Instrucciones", expanded=False)
    with instructions:
        st.write(instructions_text())

    st.write("###")  # Vertical space
    """
    # Type of info to analyze
    st.sidebar.markdown("#Menú Principal*")

    selected_data = st.sidebar.radio(label="Selecciona la opción deseada:", options=[*analysis_options], index=0,
                                     key=None)
    st.sidebar.write("#")

    #selected_subdata = st.sidebar.radio(label=f"Información de {selected_data}:",
                                       #options=[*analysis_options[selected_data]], index=0, key=None)
    st.sidebar.write("#")

    # Dates for date_input creation and delimitation
    max_date = analysis_options[selected_data]["max_date"]
    min_date = analysis_options[selected_data]["min_date"]
    start_date = analysis_options[selected_data]["start_date"]
    end_date = analysis_options[selected_data]["end_date"]

    # Markets checkboxes options
    market_options = analysis_options[selected_data]["markets"]
    demand_types_options = analysis_options[selected_data]["demand_types"]

    # Nodes multiselect
    if selected_data == "Demanda":
        # Generation info selector, only allowed one
        generation_type = st.sidebar.radio(label="Tipo de información:", options=demand_types_options)
        selected = True

        # MDa can be selected by systems, only one can be selected
        if generation_type == "Agente":
            # For multiple market selections
            markets = []
            st.sidebar.write("Tipo de mercado")
            for market in market_options:
                markets.append(st.sidebar.checkbox(market, value=False))
            check_multi_options(markets)

        # Date picker
    dates = st.sidebar.date_input('Fechas', max_value=max_date, min_value=min_date, value=(start_date, end_date))

   # Check selected options
    check_dates(dates)

    with st.sidebar:
        menu_selected = option_menu("Menu", ["About", 'Consultas'],
                               icons=['house', 'gear'], menu_icon="cast", default_index=1)
        """
        menu_selected = option_menu("App Gallery",
                             ["About", "Photo Editing", "Project Planning", "Python e-Course", "Contact"],
                             icons=['house', 'camera fill', 'kanban', 'book', 'person lines fill'],
                             menu_icon="app-indicator", default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "orange", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#02ab21"},
                             }
                             )"""

    if menu_selected == "About":
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("A cat")
            st.image("https://static.streamlit.io/examples/cat.jpg")

        with col2:
            st.header("A dog")
            st.image("https://static.streamlit.io/examples/dog.jpg")

        with col3:
            st.header("An owl")
            st.image("https://static.streamlit.io/examples/owl.jpg")
    elif menu_selected == "Consultas":
        with st.expander("See explanation"):
            st.write("""
                The chart above shows some numbers I picked for you.
                I rolled actual dice for these, so they're *guaranteed* to
                be random.
            """)
            st.image("https://static.streamlit.io/examples/dice.jpg")

    start_date, end_date = dates  # Unpack date range

    filter_df = False

# Main call
if __name__ == "__main__":
    main()