import pandas as pd

file_number = pd.read_parquet('Lib/file_number.gzip')
HH = int(input('Enter household number (1-5566): '))
num = file_number.loc[file_number['LCLid'] == HH,'file_number'].iloc[0]
print('Household number', HH, 'is in file', num)
