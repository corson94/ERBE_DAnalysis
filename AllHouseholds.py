from Model.Program import Household
from tqdm import tqdm
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


class AllHouseholds(Household):
    num_null = []
    num_points = []
    time_series = []
    index_series = []
    for i in tqdm(range(Household.number_of_Households)):
        num_null.append(Household(i).number_of_nans())
        num_points.append(Household(i).number_of_data_points())
        time_series.append(Household(i).dataframe.dropna().index)
        index_series.append(Household(i).dataframe.reset_index().dropna().index)
    df = pd.DataFrame({'num_null': num_null, 'num_points': num_points})
    df = df.loc[df.num_points != 0]
    df['HId'] = df.index
    df['null_percent'] = round(100*df.num_null/(df.num_null+df.num_points),1)

    def hist_of_nulls():
        fig = px.histogram(AllHouseholds.df.num_null)
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in
                   np.arange(0, max(AllHouseholds.df.num_null), round(max(AllHouseholds.df.num_null) / 50, -2))]
        )]
        fig.show(renderer='browser')
        return fig

    def bar_of_nulls():
        df = AllHouseholds.df.sort_values(by='num_null', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=df.index, y='num_null', hover_data=['HId','null_percent'],
                     labels={'num_null': 'Number of null entries ', 'HId': 'Household Id number ','null_percent': 'Percentage of null entries'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True,
                    range=[0, 200]
                ),
                type="linear",
                range=[0, 100]
            )
        )
        fig.show(renderer='browser')
        return fig
    def time_lines():
        buttons = []
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=AllHouseholds.time_series[0]))
        for i in tqdm(AllHouseholds.time_series):
            buttons.append(dict(label = 'HH'+str(i),
                                method = 'update',
                                args= [{'y': i}]))
        updatemenus = list([
            dict(active=1,
                 buttons = buttons)
        ])
        layout = dict(updatemenus=updatemenus)
        fig = dict(data=AllHouseholds.time_series[0].tolist(),layout=layout)



    def All_time_lines():
        fig = go.Figure()
        for i in tqdm(AllHouseholds.index_series):
            fig.add_trace(go.Scatter(y=i,visible=False))
        fig.show(renderer='browser')
        return fig