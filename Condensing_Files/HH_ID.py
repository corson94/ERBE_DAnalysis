import pandas as pd
from tqdm import tqdm
import time

def load_ID():
    start_time = time.time()
    path_in_Big = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\Data\\Raw_Data\\LCL-FullData\\CC_LCL-FullData.csv"
    ## preallocate memory for large dataframe
    file = pd.DataFrame(columns=['LCLid'], index=range(167932474), dtype='str')
    ## read csv file into dataframe
    file['LCLid'] = pd.read_csv(path_in_Big, na_values='Null', usecols=['LCLid']).astype('category')
    print('It took ', round((time.time()-start_time)/60,2), ' minutes to read this file')
    return file

def Id2numerical(dataframe:object, column='LCLid'):
    start_time = time.time()
    ## preallocate memory for large dataframe
    ID_num = pd.DataFrame(columns=['LCLid'], index=range(167932474), dtype='int64')
    ## find unique houseHold ID numbers
    HH = pd.unique(dataframe[column]).tolist()
    ## create new dataframe with houseHold ID as numerical data
    for i in tqdm(range(len(HH))):
        ID_num[column] = dataframe[column].replace(HH[i],i)
    ## save to parquet file
    ID_num.to_parquet('HH_ID.gzip')
    print('It took ', round(time.time() - start_time, 2) , 'seconds to change this column to numerical')

