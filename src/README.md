# Análisis del mercado de energía e Colombia
##  Caracerísticas del dominio (_Domain Situation_) 
Analisis del mercado de energía en Colombia. Interesados: analistas del sector del mercado de energía en Colombia. 
Intención. Idenificar patrones, comportamientos de diferentes factores de la oferta nacional

## Fuentes de información
* [Página web de indicadores SINERGOX](https://sinergox.xm.com.co/Paginas/Home.aspx)
  * Historicos
  * Información por año
  * Descargar Demanda de Energia SIN 2020, 2021, 2022. Valor Diario por todo el 2020,2021,2022
  * Demanda_comercial_por_comercializador (información diaria horaria).
* [API - desarrolladores](https://github.com/EquipoAnaliticaXM/API_XM)

## Vocabulario
* **MERCADO NO REGULADO**
: Tranzan la energía con un agente que no necesariamente va a llegar al consumidor final. Propias codiciones de negociación

* **REGULADO**
: Usuario final o distribuidor de usuario final. Tiene formulas definidas pra definir el valor de la energía. Los valores se definen con topes.  Ejm hasta 1500 kilovatios es merado regulado

## Análisis  desarrollar
### 1. HISTORICO PARTICIPACIÓN X AGENTE COMERCIALIZADOR
Histórico de  participación por agente comercializador en la demanda del SIN (Porcentaje)
Analizar la información anterior al 2020 porque en el 2020 entro la regulación en vigencia
Hipótesis: No ha habido mejoras en la participación de los agentes comercializadores pequeños en el tiempo, antes bien 
podría haber decrecido. 

#### Datos  a considerar
*  Ingresar a la api
*  Variables a revisar 
   * Demanda Comercial por agente comercializador
   * Demanda del SIN (Sistema interconectado nacional)
   * Listado de los agentes. Para identificar cuál es el agente asignado
*  Histórico de años anteriores -- Solo la primera vez 
    * En la pagina de informació del Sinergo --> Demanda comercial -->  Allí aparece por año desde el 2000. 
    * Descargar la información desde el 2014

##### Pasos proceso actual 
1. Descargar demanda comercial por comercializador. Esta es la cantidad de energía que el comercializador puso en el mercado ( lo que vendió al sistema)
2. Abrir el archivo. 
3. Sumar kilovatio hora por comercializador para el mercado **Regulado.** 
4. Sumar kilovation hora por comercializador para el mercado **NO regulado**
5. <a name="proActual5"></a> Consolidar la información de la suma diaria hora por comercializador en un nuevo archivo. 
6. Descarga la demanda comercial del SIN. La cantidad de energía que utilizó el pais Diario
7. Analizar para el archivo descargado la siguiente información:
   1. Copiar el valor del campo Demanda Energía SIN KWh en otra hoja que relacione dia y consumo
   2. Teniendo encuenta la información obtenida en el paso [5](#pasos-proceso-actual) calcular para cada dia, por comercializador y por mercado la participación en la demanda diaria del SIN (Porcentaje)
   3. Clasificar en la demanda diaria a los comercializadores teniendo encuenta la siguiente participación: 
      * Gran comercializador (>=5%)
      * Comercialización mediano (>1% y <5%)
      * comercializador pequeño ( Menor al 1%)
   4. Analizar
      * Diariamente saco lo proporcion por comercializador


#### Información para el proceso informático

##### Abstracción de tareas
* En relación a los históricos hasta el 2021, qué proporción los comercializadores pequeños han participado de la demanda del SIN antes y después del 2020?
   * ¿Cuál ha sido la tendencia de participación años?
   * ¿En relación a los anterios anteriores, la participación de los pequeños comercializadores ha incrementado, ha disminuido se ha mantenido en comparación?
   * ¿Ha mejorado la participación en el mercadeo de los pequeños comercializadores en el tiempo?
   * ¿Existe algún mes en el que consistentemente la participación de los pequeños comercializadores mejora | disminuye?
   * ¿Considrando el histórico, existe algún pequeño comercializador que tengan algún comportamiento a resaltar?

###### Acciones
  * **Analizar**.
    * _**Descubrir**_: _using vis to find new knowledge that was not previously known.. motivated by existing theories, models, hypotheses, or hunches ...to verify—or disconfirm—an existing hypothesis_
    * _**Presentar**_: _using vis for the succinct communication of information ... for telling a story with data, or guiding an audience through a series of cognitive operations... **to communicate something specific and already understood** ... the knowledge commu-
nicated is already known to the presenter in advance_
    *  _**Enjoy**_: using vis for curiosity that might be both stimulated and satisfied by the vis
  * **Produce** ddition of graphical or textual an- notations associated with one or more preexisting visualization el- ements.
    * **_Anotar_**: _addition of graphical or textual information into existing vis_
    * **_Guardar_**: _saves or captures visualization elements as persis- tent artifacts_
  * Producir datos

#### Elementos que harán parte de los gráficos
#### Claves del análisis
Información tomada de:

> Munzner, T. (2014). Visualization Analysis & Design Tamara Munzner A K Peters Visualization Series Illustrations by Eamonn Maguire. CRC Press.

* **Aggregation**
: is how and what to summarize in a way that matches well with the dataset and task.
13.3


 ## Tutorial para el uso de la API en python
https://github.com/EquipoAnaliticaXM/API_XM/blob/master/examples/data_extraction_using_pydataxm_using_library.ipynb