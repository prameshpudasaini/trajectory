import os
import zipfile
import pandas as pd

folder_name = '20221128_IndianSchool'
dir_name = os.path.join(r"D:\GitHub\trajectory\ignore\Phoenix", folder_name)
file_list = os.listdir(dir_name)

device_list = []
for file in file_list:
    device_list.append(file[5:7])

cols = ['TimeStamp', 'EventID', 'Parameter']
df = []
i = 0

for file in file_list:
    if file.endswith('.zip'):
        zip_file = os.path.join(dir_name, file)
        zf = zipfile.ZipFile(zip_file)
        temp = pd.read_csv(zf.open(zf.namelist()[0]), names = cols)
        temp['DeviceID'] = device_list[i]
        df += [temp]
    i += 1
        
output_path = dir_name + '\\' + folder_name + '.txt'

pd.concat(df, ignore_index = True).to_csv(output_path, index = False, sep = '\t')
