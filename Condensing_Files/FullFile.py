import pandas as pd
import time

# {'KWH/hh (per half hour) ': 'float64', 'DateTime': 'datetime64'})
def load_Odata():
    start_time = time.time()
    path_in_Big = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\Data\\LCL-FullData\\CC_LCL-FullData.csv"
    ## preallocate memory for large dataframe
    file = pd.DataFrame(columns=['KWH/hh (per half hour) ', 'DateTime'], index=range(167932474))
    ## read consumption column into dataframe
    file['KWH/hh (per half hour) '] = pd.read_csv(path_in_Big,na_values='Null',usecols=['KWH/hh (per half hour) ']
        ).astype({'KWH/hh (per half hour) ': 'float64'})
    ## read DateTime column into dataframe
    file['DateTime'] = pd.read_csv(path_in_Big, na_values='Null', usecols=['DateTime']
        ).astype({'DateTime': 'datetime64'})
    ## save to parquet file
    file.to_parquet('other.gzip')
    print('It took ', round((time.time()-start_time)/60,2), ' minutes to read this file')

def combine(Id_num: object, group_num: object, oData: object):
    start_time = time.time()
    ## combine 3 dataframes that make up the dataset into one dataframe
    file = pd.concat([Id_num, group_num, oData], axis=1)
    ## save to parquet file
    file.to_parquet('fullFile.gzip')
    print('It took ', round(time.time() - start_time, 2) , 'seconds to combine these dataframes')



def C_ToU(file):
    start_time = time.time()
    ## Seperate the 'std' rows into one dataframe
    Control = file[file['stdorToU'] == 0]
    ## delete the stdorToU column
    del Control['stdorToU']
    ## save to parquet file
    Control.to_parquet('Control.gzip')
    ## Seperate the 'ToU' rows into one dataframe
    ToU = file[file['stdorToU'] == 1]
    ## delete the stdorToU column
    del ToU['stdorToU']
    ## save to parquet file
    ToU.to_parquet('ToU.gzip')
    print('It took ', round((time.time()-start_time)/60,2), ' minutes to run this function')