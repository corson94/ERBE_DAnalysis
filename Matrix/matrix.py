import pandas as pd
from tqdm import tqdm
import time
import datetime


"""Takes the full data file and turns it into an x*y matrix where x is the number of households and y is time."""


def matrix(group: 'str'):
    assert group == 'Control' or group == 'ToU'
    start_time = time.time()
    path = "Data/Working_Data/One_File/Parquet_Format/"
    path_file_num = "Data/Working_Data/Seperated_Files/File_number/Lib/file_number.gzip"
    file = pd.read_parquet(path+group+'.gzip').astype({'DateTime': 'datetime64[ns]'})
    hh_num_file = pd.read_parquet(path_file_num, columns=['LCLid', 'std(0) or ToU(1)'])
    if group == 'Control':
        hh_num = hh_num_file.LCLid.loc[hh_num_file['std(0) or ToU(1)'] == 0].tolist()
    else:
        hh_num = hh_num_file.LCLid.loc[hh_num_file['std(0) or ToU(1)'] == 1].tolist()
    hh = ['HH' + str(x) for x in hh_num]

    dates = pd.DataFrame(dict(DateTime=pd.date_range(pd.to_datetime(min(file['DateTime'])),
                                                     pd.to_datetime(max(file['DateTime'])),
                                                     freq='30min')))

    hh_columns = pd.DataFrame(columns=hh, index=range(len(dates)))
    matrix_ = pd.concat([dates, hh_columns], axis=1)
    for i in tqdm(hh_num):
        date_kwh = file.loc[file['LCLid'] == i].set_index('DateTime').to_dict()['KWH/hh (per half hour) ']
        matrix_['HH' + str(i)] = matrix_['DateTime'].map(date_kwh)

    matrix_ = matrix_.set_index('DateTime')
    matrix_.to_parquet('matrix' + group[0] + '.gzip')
    matrix_.to_csv('matrix + group[0] + '.csv')
    print('It took ', round((time.time() - start_time) / 60, 2), ' minutes to run this function')
