# from Model.App.Households.Household import Household
import pandas as pd
import pickle
import datetime


def agg_day(group: str, Id: int, calculation: str = 'sum'):
    with open(rf"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT\Energy Data Analysis"
              rf"\Data\Working_Data\Pickled_objs\Households{group[0]}.pkl", 'rb') as inp:
        households = pickle.load(inp)
    df = households[Id].df
    df = pd.DataFrame({'Date': df.index, 'kWh': df.values})
    df.Date = df.Date.dt.date
    df_new = getattr(df.groupby(['Date']), calculation)()
    # matrix = pd.read_parquet(rf"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"
    #                          rf"\Energy Data Analysis\Data\Working_Data\Matrix\Original\matrix{group[0]}.gzip")
    # # matrix.insert(loc=0, column='Day', value=matrix.index)
    # matrix.reset_index(inplace=True)
    # matrix.DateTime = matrix.DateTime.dt.date
    # matrix.groupby(['DateTime']).sum()
    # # matrix.to_parquet(rf"Data/Working_Data/Matrix/Different_formats/matrix_day.gzip")
    return df_new

def AggData(group, Id, period: str, calculation = 'sum'):
    with open(rf"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT\Energy Data Analysis"
              rf"\Data\Working_Data\Pickled_objs\Households{group[0]}.pkl", 'rb') as inp:
        households = pickle.load(inp)
    df = households[Id].df
    period_format = {
        'day': 'd',
        'week': 'W-%d',
        'month': 'm'
    }
    groupby_cols = [df.DateTime.dt.year.rename('year')]
    if period == 'day':
        df_new = getattr(df.groupby([period]), calculation)()
    elif period != 'year':
        grouped = df.groupby(['year', period])[f"HH{Id}"].sum()
        df_new = pd.DataFrame(data=grouped.values,
                          index = pd.to_datetime([f"{a}-{b}-0" for a, b in grouped.index],
                                                 format=f"%Y-%{period_format[period]}-%w"),
                          columns=['kwh'])
    return df_new

def matrix_convert(group):
    df = pd.read_parquet(rf"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"
                         rf"\Energy Data Analysis\Data\Working_Data\Matrix\Original\matrix{group[0]}.gzip")
    df_date = pd.concat([df.index.to_series().dt.isocalendar(),
                         df.index.to_series().dt.month.rename('month'),
                         df], axis=1)
    df_date.day = df.index.to_series().dt.date.astype('datetime64[ns]')
    df_date.to_parquet(rf"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"
                       rf"\Energy Data Analysis\Data\Working_Data\Matrix\Different_formats\matrix_ymwd_{group[0]}")

if __name__ == '__main__':
    df, groupby_cols, grouped = AggData('Control', Id=1, period='week')
