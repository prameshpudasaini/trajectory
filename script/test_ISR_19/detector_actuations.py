import os
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

folder = r"D:\GitHub\trajectory\ignore\Phoenix\ISR_19"

def readDetectorFile(file):
    file = file
    path = os.path.join(folder, file)
    df = pd.read_csv(path)

    time_cols = ['TimeStamp', 'YST', 'RST', 'GST']
    df[time_cols] = df[time_cols].apply(pd.to_datetime, format = '%Y-%m-%d %H:%M:%S.%f')
    
    return df

sdf = readDetectorFile('20230110_1518_stop.txt') # stop-bar detector data
sdf.SSC.value_counts()

sdf = sdf.loc[sdf.SSC != 'GG'] # remove GG SSC
sdf.groupby('Parameter').SSC.value_counts()

# # decisions
# sdf.loc[sdf.SSC.isin(['YG', 'RG']), 'Decision'] = 'stop'
# sdf.loc[sdf.SSC.isin(['GY', 'YY', 'YR', 'RR']), 'Decision'] = 'go'
# sdf.groupby('Parameter').Decision.value_counts()

agg_df = sdf.groupby(['Cycle', 'Parameter']).TimeStamp.agg(['min', 'max'])
agg_df.rename(columns = {'min': 'Tmin', 'max': 'Tmax'}, inplace = True)
agg_df = agg_df.rename_axis(['Cycle', 'Parameter']).reset_index()
agg_df['Cycle'] = agg_df.Cycle.astype(int)

stop_adv_time_delta = 10
agg_df.Tmin = agg_df.Tmin - dt.timedelta(seconds = 10)

adf = readDetectorFile('20230110_1518_adv.txt') # advance detector data
# adf = adf.loc[adf.Cycle.isin(list(agg_df.Cycle.unique()))]

lane = {27: 9, 28: 10, 29: 11}
adf.Parameter = adf.Parameter.map(lane)

df = adf.merge(agg_df, on = ['Cycle', 'Parameter'], how = 'left')
df = df.loc[df.TimeStamp.between(df.Tmin, df.Tmax, inclusive = 'both'), adf.columns]

# plot

lane_pos = {9: 'R', 10: 'M', 11: 'L'}
df.Parameter = df.Parameter.map(lane_pos)
sdf.Parameter = sdf.Parameter.map(lane_pos)

df['Det'] = 'adv'
sdf['Det'] = 'stop'

mdf = pd.concat([df, sdf]).sort_values(by = 'TimeStamp').reset_index()
mdf = mdf.loc[mdf.Cycle.isin([1, 2, 3, 4, 5])]

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
    mdf, x = 'TimeStamp', y = 'Det',
    color = 'SSC',
    facet_col = 'Parameter',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()