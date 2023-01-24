import pandas as pd

from Model.AllHouseholds import AllHouseholds


def clean(group: 'str', threshold: ['int'], column: ['str']):
    """Function to clean the matrix dataset by excluding data in column x that is greater than some 'threshold'.
    Columns x can relate to any of the following:

    Number of null entries: num_null
    Maximum number of consecutive null entries: consec_nulls
    Number of zero entries: num_zeros
    Maximum number of consecutive zero entries: consec_zeros
    Total number of datapoints (including zeros, excluding NaNs): num_points
    """

    assert group == 'C' or group == 'T'
    matrix = pd.read_parquet('Data/Working_Data/Matrix/matrix' + group + '.gzip')
    groups = AllHouseholds(group)

    # if there is only one parameter and one threshold to use to clean
    if isinstance(threshold, int) and isinstance(column, str):
        cleaned = groups.df.loc[groups.df[column] <= threshold]

    # if there are multiple parameters and thresholds to use to clean
    elif isinstance(threshold, list) and isinstance(threshold, list):
        assert len(threshold) == len(column)
        cleaned = groups.df.loc[groups.df[column[0]] <= threshold[0]]
        for i in range(1,len(column)):
            cleaned = cleaned.loc[cleaned[column[i]] <= threshold[i]]

    # if there are multiple parameters to use to clean by one threshold
    elif isinstance(threshold, int) and isinstance(column, list):
        cleaned1 = groups.df.loc[groups.df[column[0]] <= threshold]
        for i in range(1,len(column)):
            cleaned = cleaned.loc[cleaned[column[i]] <= threshold]

    HH = ['HH' + str(i) for i in cleaned.HId]
    matrix_clean = matrix.loc[:,HH]
    return matrix_clean


