
from pydataxm.pydataxm import ReadDB as apiXM

class MercadoController:
    def __init__(self) -> None:
        super().__init__()

    def sumar_valores_hora(self, fila):
        """ Suma las columnas relacionadas con las horas y retorna el valor diario"""
        suma = 0.0
        # Suma las columnas de  las horas desde la hora 1 hasta la hora 24 aprovechando el indice que propone pandas
        for i in range(2, 26):
            suma = suma + fila[i]

        return suma

    def agrupar_horas_dias(self,input_df):
        # Limpiar datos para quitar NaN
        output_df = input_df.fillna(value=0)

        # Eje 1 significa que se reciben las filas
        output_df["Daily_Sum"] = output_df.apply(self.sumar_valores_hora, axis=1)

        # Quitar la parte de la hora del campo fecha
        output_df['Date'] = output_df['Date'].apply(lambda x: x.strftime("%m/%d/%Y"))
        # Guardar el resumen de los datos diarios

        # Values_code tiene el codigo que indica el elemento principal de consulta
        output_df = output_df[['Values_code', 'Date', 'Daily_Sum']]

        # Poner la fecha como el indice
        output_df.set_index('Date', inplace=True)
        return output_df