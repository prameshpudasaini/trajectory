import os
import zipfile
import pandas as pd

folder = '2023_01_ISR_19Ave'
path = os.path.join(r"D:\SynologyDrive\Data\HREB_PHX", folder)

file_list = os.listdir(path)
cols = ['TimeStamp', 'EventID', 'Parameter']
df = []

for file in file_list:
    if file.endswith('.zip'):
        zip_file = os.path.join(path, file)
        zf = zipfile.ZipFile(zip_file)
        
        temp = pd.read_csv(zf.open(zf.namelist()[0]), names = cols)
        df += [temp]
        
cdf = pd.concat(df, ignore_index = True)

cdf['TimeStamp'] = pd.to_datetime(cdf['TimeStamp'], format = '%m-%d-%Y %H:%M:%S.%f')
cdf = cdf[cdf['TimeStamp'].dt.month == 1]

output_path = os.path.join(r"D:\GitHub\trajectory\ignore\Phoenix", folder) + '.txt'
cdf.to_csv(output_path, index = False, sep = '\t')
