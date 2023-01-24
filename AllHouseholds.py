from Model.Household import Household
from tqdm import tqdm
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


class AllHouseholds(Household):

    def __init__(self, group: 'str'):
        """Returns a number of lists containing parameters of each Household within a group specified by the 'group'
        input.
        ## Lists include: ##
        Number of null values
        Maximum number of consecutive null values
        Number of zero entries
        Maximum number of consecutive zero entries
        Total number of data points

        Above 5 lists are stored in a dataframe

        ## Lists commented out as not in use: ##
        Time series without null values
        Time series but index number instead of DateTime stamp. Without null values so to compare across different
        households
        """
        self.group = group
        assert self.group == 'Control' or self.group == 'ToU'

        self.num_null = []
        self.max_consec_nulls = []
        self.num_points = []
        self.num_zeros = []
        self.max_consec_zeros = []
        # self.time_series = []
        # self.index_series = []

        if self.group == 'Control':
            self.range_of_Households = Household.range_of_CHouseholds
        elif self.group == 'ToU':
            self.range_of_Households = Household.range_of_THouseholds

        for i in tqdm(range(self.range_of_Households[0], self.range_of_Households[1])):
            self.num_null.append(Household(i).number_of_nulls())
            self.num_points.append(Household(i).number_of_data_points())
            self.num_zeros.append(Household(i).number_of_zeros())
            # self.time_series.append(Household(i).dataframe.dropna().index)
            # self.index_series.append(Household(i).dataframe.reset_index().dropna().index)
            try:
                self.max_consec_nulls.append(max(Household(i).number_of_consec_nulls(0)))
            except:
                self.max_consec_nulls.append(0)
            try:
                self.max_consec_zeros.append(max(Household(i).number_of_consec_zeros(0)))
            except:
                self.max_consec_zeros.append(0)
        df = pd.DataFrame({'num_null': self.num_null,
                           'consec_nulls': self.max_consec_nulls,
                           'num_points': self.num_points,
                           'num_zeros': self.num_zeros,
                           'consec_zeros': self.max_consec_zeros})
        df = df.loc[df.num_points != 0]
        df['HId'] = df.index
        df['null_percent'] = round(100*df.num_null/(df.num_null+df.num_points),1)
        df['zeros_percent'] = round(100 * df.num_zeros / df.num_points, 1)
        self.df = df


    def hist_of_nulls(self, number_of_bins=50):
        """Histogram of number of null entries."""
        fig = px.histogram(self.df.num_null)
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in
                   np.arange(0, max(self.df.num_null), round(max(self.df.num_null) / number_of_bins, -2))]
        )]
        fig.show(renderer='browser')
        return fig

    def bar_of_nulls(self, number_of_HH=200):
        """Bar chart showing the number of null values for each household in descending order.
        'number_of_HH' input represents the top x households that are displayed."""
        df = self.df.sort_values(by='num_null', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=self.df.index, y='num_null', hover_data=['HId','null_percent'],
                     labels={'num_null': 'Number of null entries ', 'HId': 'Household Id number ',
                             'null_percent': 'Percentage of null entries', 'x': 'Index'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True,
                    range=[0, number_of_HH]
                ),
                type="linear",
                range=[0, number_of_HH]
            )
        )
        fig.show(renderer='browser')
        return fig

    def bar_of_consec_nulls(self,number_of_HH=200):
        """Bar chart showing the maximum number of consecutive null values for each household in descending order.
                'number_of_HH' input represents the top x households that are displayed."""
        df = self.df.sort_values(by='consec_nulls', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=self.df.index, y='consec_nulls', hover_data=['HId', 'num_null', 'null_percent'],
                     labels={'num_null': 'Number of null entries ', 'HId': 'Household Id number ',
                             'null_percent': 'Percentage of null entries', 'x': 'Index',
                             'consec_nulls': 'Maximum number of consecutive null entries'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True,
                    range=[0, number_of_HH]
                ),
                type="linear",
                range=[0, round(number_of_HH/2,0)]
            )
        )
        fig.show(renderer='browser')
        return fig

    def bar_of_zeros(self, number_of_HH=200):
        """Bar chart showing the number of zero entries for each household in descending order.
                'number_of_HH' input represents the top x households that are displayed."""
        df = self.df.sort_values(by='num_zeros', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=df.index, y='num_zeros', hover_data=['HId', 'zeros_percent'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries', 'x': 'Index'})
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

    def bar_of_consec_zeros(self, number_of_HH=200):
        """Bar chart showing the maximum number of consecutive zero entries for each household in descending order.
                        'number_of_HH' input represents the top x households that are displayed."""
        df = self.df.sort_values(by='consec_zeros', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=self.df.index, y='consec_zeros', hover_data=['HId', 'num_zeros', 'zeros_percent'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries', 'x': 'Index',
                             'consec_zeros': 'Maximum number of consecutive zero entries'},
                     text='HId')
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

    def bar_of_zeros_percent(self, number_of_HH=200):
        """Bar chart showing the percentage of zero entries for each household in descending order.
                      'number_of_HH' input represents the top x households that are displayed."""
        df = self.df.sort_values(by='zeros_percent', ascending=False).reset_index(drop=True)
        fig = px.bar(df, x=df.index, y='zeros_percent', hover_data=['HId', 'num_zeros'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries' ,'x': 'Index'})
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

    """def time_lines():
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
        return fig"""