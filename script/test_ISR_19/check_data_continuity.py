import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

def checkDataContinuity(day):
    file = '2023_01_ISR_19Ave.txt'
    path = os.path.join(r"D:\GitHub\trajectory\ignore\Phoenix", file)
    
    df = pd.read_csv(path, sep = '\t')
    
    # filter events and parameters
    det = (9, 10, 11, 27, 28, 29)
    df.query('EventID == 82 and Parameter in @det', inplace = True)
    df.drop('EventID', axis = 1, inplace = True)
    
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format = '%Y-%m-%d %H:%M:%S.%f')
    df = df[df['TimeStamp'].dt.day == day]
    
    fig = px.scatter(df, x = 'TimeStamp', y = 'Parameter')
    fig.show()
