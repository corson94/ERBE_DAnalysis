import os
from tqdm import tqdm
import pandas as pd
import time

## split csv file into chunks of 1 million rows and save to individual parquet files ##

start_time = time.time()
n = 1
HH_file = pd.DataFrame()
for chunk in tqdm(pd.read_csv('Data/Working_Data/One_File/CSV_Format/Control.csv', chunksize = 1000000)):
    ## find unique houseHold ID numbers
    HH = pd.DataFrame(pd.unique(chunk['LCLid']), columns=['LCLid'])
    ## file number iterated over with each file
    HH['file_number'] = n
    ## combine houseHold numbers and file numbers with those from previous files
    HH_file = pd.concat([HH_file, HH], ignore_index=True).drop_duplicates(subset='LCLid')
    #filename_csv = 'Data_Files/file' + str(n) + '.csv'
    #filename_p = 'Data_Files2/file' + str(n) + '.gzip'
    ## save to parquet and csv file
    #chunk.to_csv(filename_csv, index=False)
    #chunk.to_parquet(filename_p)
    n +=1

HH_file.to_parquet('file_numberC.gzip')
print('It took ', round((time.time()-start_time)/60,2), ' minutes to run this function')