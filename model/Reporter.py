from pydataxm import pydataxm

import BaseConocimientoXM as bdXM

from util.Settings import ConsultasXMEnum


class Reporter:

    def __init__(self):
        self.apiXM = bdXM.BaseConocimientoXM()
        self.consultas = [ConsultasXMEnum.DEMANDA_SIN_OPC, ConsultasXMEnum.DEMANDA_COMERCIAL_NO_REGULADA_OPC, ConsultasXMEnum.DEMANDA_COMERCIAL_REGULADA_OPC, ConsultasXMEnum.DEMANDA_TOTAL_AGENTES_OPC]

    def test(self, metrica, agente, fecha_inicial, fecha_final):
        df_temp = self.apiXM.request_data(pydataxm.ReadDB(), metrica, agente, fecha_inicial, fecha_final)
        return df_temp

