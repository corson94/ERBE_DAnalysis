import pandas as pd
import plotly.express as px
import datetime

"""These functions find the time stamps that are not either 30:00 or 00:00 (MM:SS), which all happen to be nulls. """

def matrix_wt(group: 'str'):
    assert group == 'Control' or group == 'ToU'
    file = pd.read_parquet('Data/Working_Data/One_File/Parquet_Format/' + group + '.gzip')
    file_rt = file[
        (((file.DateTime.dt.minute == 0) | (file.DateTime.dt.minute == 30)) & (file.DateTime.dt.second == 0))]
    file_wt = file[~file.isin(file_rt).DateTime]
    file_wt.to_parquet('file_wt_' + group[0] + '.gzip')


def plot_wt(group: 'str'):
    assert group == 'Control' or group == 'ToU'
    file = pd.read_parquet('Data/Working_Data/Matrix/Original/Wrong_Time_Nulls/file_wt_' + group[0] + '.gzip')
    df_all = file.sort_values(by='DateTime', ignore_index=True)
    fig_all = px.scatter(df_all, x=df_all.index, y='DateTime')
    df_min = df_all[(df_all.DateTime.dt.year == 2012) & (df_all.DateTime.dt.day == 18)]
    fig_min = px.scatter(df_min, x=df_min.index, y='DateTime')
    # fig_maj.show(renderer='browser')
    # fig_min.show(renderer='browser')
    fig_all.write_html('Data/Figures/AllHouseholds/' + group[0] + '/fig_wt_all.html')
    fig_min.write_html('Data/Figures/AllHouseholds/' + group[0] + '/fig_wt_min.html')
