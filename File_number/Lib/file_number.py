import pandas as pd
import os



file_number = pd.read_parquet('file_number.gzip')
HH = int(input('Enter houseHold number (1-5566): '))
num = file_number.loc[file_number['LCLid'] == HH,'file_number'].iloc[0]
C_ToU = file_number['std(0) or ToU(1)'].loc[HH]
#name = file_number.loc[file_number[''] == HH,'file_number'].iloc[0]
print('Household number: ' + str(HH) + '/nFile number: ' + str(num) + '/n Control or ToU: ' + str(C_ToU))
