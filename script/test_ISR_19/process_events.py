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
rst = tuple((pdf.loc[pdf['EventID'] == 10])['TimeStamp']) # red
gst = tuple((pdf.loc[pdf['EventID'] == 1])['TimeStamp']) # green

Cycle = tuple(range(1, len(yst)))
CycleLen = Vector(yst[1:]) - Vector(yst[:-1])

RedTime = Vector(gst) - Vector(rst)
GreenTime = Vector(yst[1:]) - Vector(gst)

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

# lane-specific parameters computation
def computeParameters(lane):
    ldf = ddf.copy(deep = True)
    ldf.query('Parameter == @lane', inplace = True) # lane-based df
    
    det_on = tuple((ldf.loc[ldf['EventID'] == 82])['TimeStamp'])
    det_off = tuple((ldf.loc[ldf['EventID'] == 81])['TimeStamp'])
    
    # filter df for timestamp between first det on and last det off
    first_det_on, last_det_off = min(det_on), max(det_off)
    ldf = ldf[(ldf['TimeStamp'] >= first_det_on) & (ldf['TimeStamp'] <= last_det_off)]
    
    # compute parameters
    ODT = Vector(det_off) - Vector(det_on) # on-detector time

    lead_headway = Vector(det_on[1:]) - Vector(det_on[:-1]) # leading headway
    lead_headway.append(None)
    fol_headway = lead_headway[-1:] + lead_headway[:-1] # following headway

    lead_gap = Vector(det_on[1:]) - Vector(det_off[:-1]) # leading gap
    lead_gap.append(None)
    fol_gap = lead_gap[-1:] + lead_gap[:-1] # following gap
    
    return {'ODT': ODT,
            'lead_headway': lead_headway, 
            'fol_headway': fol_headway,
            'lead_gap': lead_gap,
            'fol_gap': fol_gap}

# =============================================================================
# merge events data sets
# =============================================================================

mdf = pd.concat([pdf, ddf]).sort_values(by = 'TimeStamp')
mdf = mdf[:-1]

# add signal category
signal = {8: 'Y', 10: 'R', 1: 'G'}
mdf['Signal'] = mdf['EventID'].map(signal)

# add phase data: cycle, cycle length, indication timestamps, indication intervals
phase_cols = {'Cycle': Cycle,
              'CycleLen': CycleLen,
              'YST': yst[:-1],
              'RST': rst,
              'GST': gst,
              'RedTime': RedTime,
              'GreenTime': GreenTime}

for key, value in phase_cols.items():
    mdf.loc[mdf['EventID'] == 8, key] = value

# forward fill new columns
fill_cols = [col for col in phase_cols.keys()]
fill_cols.append('Signal')

for col in fill_cols: 
    mdf[col].ffill(inplace = True)

# other phase-detection parameters
mdf['AIC'] = (mdf['TimeStamp'] - mdf['YST']).dt.total_seconds() # arrival in cycle
mdf['TUG'] = (mdf['GST'] - mdf['TimeStamp']).dt.total_seconds() # time until green

# signal status change
def computeSSC(lane):
    detOn = (mdf.loc[(mdf['EventID'] == 82) & (mdf['Parameter'] == lane)])['Signal'].tolist()
    detOff = (mdf.loc[(mdf['EventID'] == 81) & (mdf['Parameter'] == lane)])['Signal'].tolist()
    return [i + j for i, j in zip(detOn, detOff)]

for lane in det_stop:
    mdf.loc[(mdf['EventID'] == 82) & (mdf['Parameter'] == lane), 'SSC'] = computeSSC(lane)

# filter only detection 'on' events
mdf.query('EventID == 82', inplace = True)
mdf.drop('EventID', axis = 1, inplace = True)

# add det data: ODT, headway, gap
det_cols = ['ODT', 'lead_headway', 'fol_headway', 'lead_gap', 'fol_gap']

for col in det_cols:
    for lane in det_stop:
        mdf.loc[mdf['Parameter'] == lane, col] = computeParameters(lane)[col]
