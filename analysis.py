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
    df['tone_name'] = df['tone_name'].replace('Happiness', 3) 

    #calculamos el nuevo score
    df['new_score'] = df['tone_name'] + df['score']
    #seleccionamos lo que queremos analizar
    selected = df[['new_score']]
    #calculamos coeficientes de pendiente y la Distancia media cuadrática mínima
    coefficients, residuals, _, _, _ = np.polyfit(range(len(selected.index)),selected,1,full=True)
    #error cuadratico medio
    mse = residuals[0]/(len(selected.index))
    #Error cuadrático medio normalizado
    nrmse = np.sqrt(mse)/(selected.max() - selected.min())
    #pendiente
    pendiente = coefficients[0]

    plt.plot([coefficients[0]*x + coefficients[1] for x in range(len(selected))])
    plt.savefig('files/analisis.png', bbox_inches='tight')
    #variacion
    cv2 = ss.variation(df["new_score"])
    #asimetria
    asimetria = ss.skew(df["new_score"])
    d = {'pendiente': pendiente[0], 'variacion': cv2, 'asimetria': asimetria}
    print(d)
    
    return d