from tqdm import tqdm
from pandas import pd

## split csv file into chunks of 1 million rows and save to individual parquet files ##

n = 1
HH_file = pd.DataFrame()
for chunk in tqdm(pd.read_csv('Control.csv', chunksize = 1000000)):
    ## find unique household ID numbers
    HH = pd.DataFrame(pd.unique(chunk['LCLid']), columns=['LCLid'])
    ## file number iterated over with each file
    HH['file_number'] = n
    ## combine household numbers and file numbers with those from previous files
    HH_file = pd.concat([HH_file, HH], ignore_index=True).drop_duplicates(subset='LCLid')
    filename = 'Data_Files/file' + str(n) + 'gzip'
    ## save to parquet file
    chunk.to_parquet(filename)
    n +=1

