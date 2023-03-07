import os
import pandas as pd
from datetime import datetime

class Vector():
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        return repr(self.data)
    def __sub__(self, other):
        return list((a-b).total_seconds() for a, b in zip(self.data, other.data))

folder = r"D:\GitHub\trajectory\ignore\Phoenix\ISR_19"
file = '2023_01_ISR_19Ave.txt'
path = os.path.join(folder, file)

df = pd.read_csv(path, sep = '\t')
df.TimeStamp = pd.to_datetime(df.TimeStamp, format = '%Y-%m-%d %H:%M:%S.%f').sort_values()

# input parameters
year, month, day = 2023, 1, 11
from_hour, to_hour = 7, 9
det_type = 'adv'

det = (9, 10, 11) if det_type == 'stop' else (27, 28, 29)

# filter timestamp
from_time = datetime(year, month, day, from_hour)
to_time = datetime(year, month, day, to_hour)
df = df[(df.TimeStamp >= from_time) & (df.TimeStamp <= to_time)]

# =============================================================================
# signal phase change events
# =============================================================================

phase = 2 # phase config
pce = (7, 8, 9, 10, 11, 1) # phase change events

pdf = df.copy(deep = True) # phase change events data frame
pdf = pdf[(pdf.Parameter == phase) & (pdf.EventID.isin(pce))]

# assumption: cycle start on yellow
minCycleTime = min((pdf.loc[pdf.EventID == 7]).TimeStamp)
maxCycleTime = max((pdf.loc[pdf.EventID == 7]).TimeStamp)

pdf = pdf[(pdf.TimeStamp >= minCycleTime) & (pdf.TimeStamp <= maxCycleTime)]
pdf = pdf[pdf.EventID.isin((8, 10, 1))]

# indication start times
yst = tuple((pdf.loc[pdf.EventID == 8]).TimeStamp) # yellow
rst = tuple((pdf.loc[pdf.EventID == 10]).TimeStamp) # red
gst = tuple((pdf.loc[pdf.EventID == 1]).TimeStamp) # green

print("Yellows, Red, Greens:", len(yst), len(rst), len(gst), "\n")

Cycle = tuple(range(1, len(yst)))
CycleLen = Vector(yst[1:]) - Vector(yst[:-1])

YellowTime = Vector(rst) - Vector(yst[:-1])
RedTime = Vector(gst) - Vector(rst)
GreenTime = Vector(yst[1:]) - Vector(gst)

print("Min, max of phase parameters:")
print("Cycle length:", min(CycleLen), max(CycleLen))
print("Yellow time:", min(YellowTime), max(YellowTime))
print("Red time:", min(RedTime), max(RedTime))
print("Green time:", min(GreenTime), max(GreenTime), "\n")

# =============================================================================
# detector actutation events
# =============================================================================

ddf = df.copy(deep = True) # actutation events data frame
ddf = ddf[(ddf.EventID.isin((81, 82))) & (ddf.Parameter.isin(det))]
ddf = ddf[(ddf.TimeStamp > minCycleTime) & (ddf.TimeStamp < maxCycleTime)]

# count lane-by-lane detections
print(ddf.Parameter.value_counts(dropna = False).sort_values(), "\n")
print(ddf.groupby('Parameter').EventID.value_counts())

# lane-specific parameters computation
def computeParameters(lane):
    ldf = ddf.copy(deep = True) # lane-based acutation events data frame
    ldf = ldf[(ldf.Parameter == lane)]
    
    det_on = tuple((ldf.loc[ldf.EventID == 82]).TimeStamp)
    det_off = tuple((ldf.loc[ldf.EventID == 81]).TimeStamp)
    
    # filter data frame for timestamp between first det on and last det off
    first_det_on, last_det_off = min(det_on), max(det_off)
    ldf = ldf[(ldf.TimeStamp >= first_det_on) & (ldf.TimeStamp <= last_det_off)]
    
    # compute parameters
    ODT = Vector(det_off) - Vector(det_on) # on-detector time
    
    lead_headway = Vector(det_on[1:]) - Vector(det_on[:-1]) # leading headway
    lead_headway.append(None)
    fol_headway = lead_headway[-1:] + lead_headway[:-1] # following headway
    
    lead_gap = Vector(det_on[1:]) - Vector(det_off[:-1]) # leading gap
    lead_gap.append(None)
    fol_gap = lead_gap[-1:] + lead_gap[:-1] # following gap
    
    return{'ODT': ODT,
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
mdf['Signal'] = mdf.EventID.map(signal)

# phase data: cycle, cycle length, indication timestamps, indication intervals
phase_cols = {'Cycle': Cycle,
              'CycleLen': CycleLen,
              'YST': yst[:-1],
              'RST': rst,
              'GST': gst,
              'RedTime': RedTime,
              'GreenTime': GreenTime}

for key, value in phase_cols.items():
    mdf.loc[mdf.EventID == 8, key] = value

# forward fill new columns
fill_cols = [col for col in phase_cols.keys()]
fill_cols.append('Signal')

for col in fill_cols:
    mdf[col].ffill(inplace = True)
    
# phase & detection parameters
mdf['AIC'] = (mdf.TimeStamp - mdf.YST).dt.total_seconds() # arrival in cycle
mdf['TUG'] = (mdf.GST - mdf.TimeStamp).dt.total_seconds() # time until green

# signal status change
def computeSSC(lane):
    detOn = tuple((mdf.loc[(mdf.EventID == 82) & (mdf.Parameter == lane)]).Signal)
    detOff = tuple((mdf.loc[(mdf.EventID == 81) & (mdf.Parameter == lane)]).Signal)
    return [i + j for i, j in zip(detOn, detOff)]

for lane in det:
    mdf.loc[(mdf.EventID == 82) & (mdf.Parameter == lane), 'SSC'] = computeSSC(lane)

# filter only detection 'on' events
mdf = mdf[mdf.EventID == 82]
mdf.drop('EventID', axis = 1, inplace = True)

# add detection parameters: ODT, headway, gap
det_cols = ['ODT', 'lead_headway', 'fol_headway', 'lead_gap', 'fol_gap']

for col in det_cols:
    for lane in det:
        mdf.loc[mdf.Parameter == lane, col] = computeParameters(lane)[col]

output_file = str(year) + str(month).zfill(2) + str(day).zfill(2) + '_'
output_file += str(from_hour).zfill(2) + str(to_hour).zfill(2) + '_'
output_file += det_type

output_path = os.path.join(r"D:\GitHub\trajectory\ignore\Phoenix\ISR_19", output_file) + '.txt'
mdf.to_csv(output_path, index = False)
