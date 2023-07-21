import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

folder = r"D:\GitHub\trajectory\ignore\Phoenix\ISR_19"

def detectorDF(file):
    file = file
    path = os.path.join(folder, file)
    df = pd.read_csv(path)

    time_cols = ['TimeStamp', 'YST', 'RST', 'GST']
    df[time_cols] = df[time_cols].apply(pd.to_datetime, format = '%Y-%m-%d %H:%M:%S.%f')
    
    return df
    
df_adv = detectorDF('20230110_1518_adv.txt')
df_stop = detectorDF('20230110_1518_stop.txt')

dist_adv_stop = 260
len_det_adv = 5
len_det_stop = 40

# def matchEvent(adv_index, stop_index):
#     time_diff = (df_stop.TimeStamp[stop_index] - df_adv.TimeStamp[adv_index]).total_seconds()
#     print("Time difference:", time_diff)
    
#     speed = round(dist_adv_stop / time_diff, 2)
#     print("Speed:", speed, "ft/s,", round(speed * 3600/5280, 2), "mph")
    
#     acc = round(speed / time_diff, 2)
#     print("Acceleration:", acc, "ft/s2")
    
#     speed_adv = round(len_det_adv / df_adv.ODT[adv_index])
#     print("Speed over advance detector:", speed_adv)
    
#     speed_stop = round(len_det_stop / df_stop.ODT[stop_index])
#     print("Speed over stop-bar detector:", speed_stop, "\n")
    
# matchEvent(53, 39)
# matchEvent(52, 40)

# update parameter to lane position
det_adv = (27, 28, 29)
det_stop = (9, 10, 11)

lane_adv = {27: 'R', 28: 'M', 29: 'L'}
lane_stop = {9: 'R', 10: 'M', 11: 'L'}

df_adv.Parameter = df_adv.Parameter.map(lane_adv)
df_stop.Parameter = df_stop.Parameter.map(lane_stop)

df_adv['Det'] = 'adv'
df_stop['Det'] = 'stop'

df = pd.concat([df_adv, df_stop]).sort_values(by = 'TimeStamp').reset_index()

df = df.loc[df.Cycle.isin([1, 2, 3, 4, 5])]

# scatter plot of actuations at advance & stop-bar locations
cat_order = {'SSC': ['YY', 'YR', 'RR', 'RG', 'GG', 'GY', 'GR'],
             'Parameter': ['L', 'M', 'R']}
ssc_color = {'YY': 'orange',
             'YR': 'brown',
             'RR': 'red',
             'RG': 'black',
             'GG': 'green',
             'GY': 'limegreen',
             'GR': 'navy'}

px.scatter(
    df, x = 'TimeStamp', y = 'Det',
    color = 'SSC',
    facet_col = 'Parameter',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()

def matchEvent(adv_index, stop_index):
    time_diff = (df.TimeStamp[stop_index] - df.TimeStamp[adv_index]).total_seconds()
    print("Time difference:", time_diff)
    
    speed = round(dist_adv_stop / time_diff, 2)
    print("Speed:", speed, "ft/s,", round(speed * 3600/5280, 2), "mph")
    
    acc = round(speed / time_diff, 2)
    print("Acceleration:", acc, "ft/s2")
    
    speed_adv = round(len_det_adv / df.ODT[adv_index])
    print("Speed over advance detector:", speed_adv)
    
    speed_stop = round(len_det_stop / df.ODT[stop_index])
    print("Speed over stop-bar detector:", speed_stop, "\n")
    
matchEvent(103, 105)
matchEvent(108, 112)

matchEvent(106, 109)
matchEvent(101, 107)
matchEvent(101, 104)

rdf = df.loc[df.Parameter == 'R']
mdf = df.loc[df.Parameter == 'M']
ldf = df.loc[df.Parameter == 'L']

# px.scatter(
#     df, x = 'ODT', y = 'fol_gap', 
#     color = 'SSC',
#     facet_col = 'Parameter',
#     category_orders = cat_order,
#     color_discrete_map = ssc_color
# ).show()

df_stop.groupby('Parameter').SSC.value_counts()
df_adv.groupby('Parameter').SSC.value_counts()
