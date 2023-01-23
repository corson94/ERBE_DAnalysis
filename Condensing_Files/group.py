import pandas as pd
import time
import fastparquet

# {'KWH/hh (per half hour) ': 'float64', 'DateTime': 'datetime64'})
def load_group():
    start_time = time.time()
    path_in_Big = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\Data\\LCL-FullData\\CC_LCL-FullData.csv"
    ## preallocate memory for large dataframe
    file = pd.DataFrame(columns=['stdorToU'], index=range(167932474), dtype='str')
    ## read csv file into dataframe
    file['stdorToU'] = pd.read_csv(path_in_Big, na_values='Null', usecols=['stdorToU']).astype('category')
    print('It took ', round((time.time()-start_time)/60,2), ' minutes to read this file')
    return file

def group2numerical(dataframe: object):
    start_time = time.time()
    ## preallocate memory for large dataframe
    group_num = pd.DataFrame(columns=['stdorToU'], index=range(167932474), dtype='int8')
    ## replace strings with numerical data and add to new dataframe
    group_num['stdorToU'] = dataframe.replace({'Std':0, 'ToU':1})
    ## save to parquet file
    group_num.to_parquet('group.gzip')
    print('It took ', round(time.time() - start_time, 2), 'seconds to change this column to numerical')
