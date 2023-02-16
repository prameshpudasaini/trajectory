import pandas as pd

class Vector():
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return repr(self.data)
    def __sub__(self, other):
        return list(((a-b).total_seconds() for a, b in zip(self.data, other.data)))

path = r"D:\GitHub\trajectory\ignore\Phoenix\20221214_IndianSchool.txt"
df = pd.read_csv(path, sep = '\t')

df.query('DeviceID == 46', inplace = True) # filter intersection
df.drop('DeviceID', axis = 1, inplace = True)

# filter timestamp
start_time, end_time = '2022-12-14 07:40:00.0', '2022-12-14 08:20:00.0'
df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format = '%m-%d-%Y %H:%M:%S.%f').sort_values()
df = df[(df['TimeStamp'] > start_time) & (df['TimeStamp'] < end_time)]

# check unique values
df['EventID'].unique()
df['Parameter'].unique()

# =============================================================================
# signal phase change events
# =============================================================================

phase = 2 # phase config
pce = (7, 8, 9, 10, 11, 1) # phase change events

pdf = df.copy(deep = True) # phase change events data frame
pdf.query('EventID in @pce and Parameter == @phase', inplace = True)

# assumption: cycle starts on yellow
minCycleTime = min((pdf.loc[pdf['EventID'] == 7])['TimeStamp'])
maxCycleTime = max((pdf.loc[pdf['EventID'] == 7])['TimeStamp'])

pdf = pdf[(pdf['TimeStamp'] >= minCycleTime) & (pdf['TimeStamp'] <= maxCycleTime)]
pdf.query('EventID in [8, 10, 1]', inplace = True)

# indication start times
yst = tuple((pdf.loc[pdf['EventID'] == 8])['TimeStamp']) # yellow
rst = tuple((pdf.loc[pdf['EventID'] == 10])['TimeStamp']) # green
gst = tuple((pdf.loc[pdf['EventID'] == 1])['TimeStamp']) # red

Cycle = tuple(range(1, len(yst) + 1))
CycleLen = Vector(yst[1:]) - Vector(yst[:-1])
CycleLen.append(None)

GreenTime = Vector(gst) - Vector(yst[:-1])
GreenTime.append(None)

# =============================================================================
# detector actutation events
# =============================================================================

det_stop = (9, 10, 11)
det_adv = (27, 28, 29)

ddf = df.copy(deep = True) # actutation events data frame
ddf.query('EventID in (81, 82) and Parameter in @det_stop', inplace = True)
ddf = ddf[(ddf['TimeStamp'] > minCycleTime) & (ddf['TimeStamp'] < maxCycleTime)]

# count lane-by-lane detections
ddf['Parameter'].value_counts(dropna = False).sort_values()    
ddf.groupby(['Parameter'])['EventID'].value_counts()

ddf9 = ddf.copy(deep = True)
ddf9.query('Parameter == 11', inplace = True)

# filter df for timestamp between first det on and last det off
det_on = tuple((ddf9.loc[ddf9['EventID'] == 82])['TimeStamp'])
det_off = tuple((ddf9.loc[ddf9['EventID'] == 81])['TimeStamp'])

first_det_on, last_det_off = min(det_on), max(det_off)

ddf9 = ddf9[(ddf9['TimeStamp'] >= first_det_on) & (ddf9['TimeStamp'] <= last_det_off)]

# compute parameters
ODT = Vector(det_off) - Vector(det_on) # on-detector time

lead_headway = Vector(det_on[1:]) - Vector(det_on[:-1]) # leading headway
lead_headway.append(None)
fol_headway = lead_headway[-1:] + lead_headway[:-1] # following headway

lead_gap = Vector(det_on[1:]) - Vector(det_off[:-1]) # leading gap
lead_gap.append(None)
fol_gap = lead_gap[-1:] + lead_gap[:-1] # following gap