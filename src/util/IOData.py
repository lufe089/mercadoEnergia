import pandas as pd
from enum import Enum

def exportar_df_xlsx(df, file_path, index=False):
    # Index false evita que ponga el indice adiciona
    df.to_excel(file_path, index=index)

def leer_xlsx_to_df(file_path):
    df = pd.read_excel(file_path)
    return df