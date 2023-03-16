import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

folder = r"D:\GitHub\trajectory\ignore\Phoenix\ISR_19"
file = '20230110_1518_stop.txt'
path = os.path.join(folder, file)
df = pd.read_csv(path)

time_cols = ['TimeStamp', 'YST', 'RST', 'GST']
df[time_cols] = df[time_cols].apply(pd.to_datetime, format = '%Y-%m-%d %H:%M:%S.%f')

# arrival in cycle as percentage
df['AIC_perc'] = (df.AIC / df.CycleLen).round(4)

print(df.Parameter.value_counts())
print(df.SSC.value_counts())

cat_order = {'SSC': ['YY', 'YR', 'RR', 'RG', 'GG', 'GY', 'GR'],
             'Parameter': sorted(list(df.Parameter.unique()))}
ssc_color = {'YY': 'orange',
             'YR': 'brown',
             'RR': 'red',
             'RG': 'black',
             'GG': 'green',
             'GY': 'limegreen',
             'GR': 'navy'}

# distribution of cycle length
px.bar(
    df, x = 'Cycle', y = 'CycleLen'
).show()

# distribution of arrivals in a cycle
px.histogram(
    df, x = 'AIC_perc',
    nbins = 100
).show()

px.histogram(
    df, x = 'AIC_perc',
    nbins = 50,
    facet_col = 'Parameter',
    category_orders = cat_order
).show()

px.histogram(
    df, x = 'AIC_perc',
    nbins = 50,
    facet_col = 'Signal',
    category_orders = cat_order,
).show()

px.scatter(
    df, x = 'ODT', y = 'fol_gap', 
    color = 'SSC',
    facet_col = 'Parameter',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()

px.box(
       df, x = 'SSC', y = 'ODT',
       color = 'SSC',
       facet_col = 'Parameter',
       category_orders = cat_order,
       color_discrete_map = ssc_color
).show()

px.scatter(
    df, x = 'ODT', y = 'AIC',
    color = 'SSC',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()

px.scatter(
    df, x = 'ODT', y = 'TUG',
    color = 'SSC',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()

px.scatter(
    df, x = 'AIC', y = 'TUG',
    color = 'SSC',
    category_orders = cat_order,
    color_discrete_map = ssc_color
).show()
