from flask.wrappers import Response
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats as ss
import json
from pandas import json_normalize
from datetime import datetime
import base64
from os import remove

def singleQuoteToDoubleQuote(singleQuoted):
            cList=list(singleQuoted)
            inDouble=False;
            inSingle=False;
            for i,c in enumerate(cList):
                if c=="'":
                    if not inDouble:
                        inSingle=not inSingle
                        cList[i]='"'
                elif c=='"':
                    inDouble=not inDouble
            doubleQuoted="".join(cList)    
            return doubleQuoted

def find_tendencies(data):
    data = str(data)
    data = singleQuoteToDoubleQuote(data)
    
    info = json.loads(data)
    
    df = pd.DataFrame()

    for i in info:
        t = i['sentiment']['document_tone']['tones']
        date = { 'date': datetime.fromtimestamp(i['date']['_seconds']).strftime(" %d/%m/%Y %I:%M:%S")}
        for x in t:
            x.update(date)
        df = pd.concat([df,json_normalize(t[0])])
    
    df.index = range(df.shape[0])
    df.index = df['date']

    #Cambiamos los nombres por los indices de cada estado de ánimo
    df['tone_name'] = df['tone_name'].replace('Sadness', 0)
    df['tone_name'] = df['tone_name'].replace('Anger', 1)
    df['tone_name'] = df['tone_name'].replace('Fear', 2) 
    df['tone_name'] = df['tone_name'].replace('Joy', 3) 

    #calculamos el nuevo score
    df['new_score'] = df['tone_name'] + df['score']
    #seleccionamos lo que queremos analizar
    selected = df[['new_score']]
    
    #plt.savefig('files/voyprimera.png')
    #calculamos coeficientes de pendiente y la Distancia media cuadrática mínima
    coefficients, residuals, _, _, _ = np.polyfit(range(len(selected.index)),selected,1,full=True)
    #error cuadratico medio
    mse = residuals[0]/(len(selected.index))
    #Error cuadrático medio normalizado
    nrmse = np.sqrt(mse)/(selected.max() - selected.min())
    #pendiente
    pendiente = coefficients[0]
    #plotear
    selected.plot()
    plt.plot([coefficients[0]*x + coefficients[1] for x in range(len(selected))])
    #modificar la leyenda
    plt.legend(['Estado anímico'])
    #arreglamos etiquetas del eje x
    plt.xticks(rotation=45, ha="right")
    #cambiamos date por fecha
    plt.xlabel("Fechas")
    #guardar la imagen
    plt.savefig('files/analisis.png', bbox_inches='tight')
    #limpiar el plt
    plt.clf()
    #variacion
    cv2 = ss.variation(df["new_score"])
    #asimetria
    asimetria = ss.skew(df["new_score"])
    
    with open("files/analisis.png", "rb") as image_file:
        encoded_string= image_file.read()

    # second: base64 encode read data
    # result: bytes (again)
    base64_bytes = base64.b64encode(encoded_string)

    # third: decode these bytes to text
    # result: string (in utf-8)
    base64_string = base64_bytes.decode('utf-8')

    d = {"pendiente": pendiente[0], "variacion": cv2, "asimetria": asimetria, "image": base64_string}
    
    return d