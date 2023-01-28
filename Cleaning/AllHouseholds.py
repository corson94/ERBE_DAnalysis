import os
import inspect
from tqdm import tqdm
import plotly.express as px
# import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime

from Model.Cleaning.Household import Household

slider = False

class AllHouseholds(Household):
    """Brings together data from all households within a 'group' by calling on the Household module in order to
    analyse all of them together. Used to determine the extent of the number of NaNs and zeros within the dataset.

    Call in 'AllHouseholds('group') where 'group' can equal either 'Control' or 'ToU'. Then any of the following
    functions can be called to plot the relevant data."""

    load_data_all = [False, False]
    file_all = [(), ()]

    def __init__(self, group: 'str'):
        """Returns a number of lists containing parameters of each Household within a group specified by the 'group'
        input.
        ## Lists include: ##
        Number of null values
        Maximum number of consecutive null values
        Number of zero entries
        Maximum number of consecutive zero entries
        Total number of data points

        Above 5 lists are stored in a df

        ## Lists commented out as not in use: ##
        Time series without null values
        Time series but index number instead of DateTime stamp. Without null values so to compare across different
        households
        """
        self.group = group
        assert self.group == 'Control' or self.group == 'ToU'
        self.group_num = Household.groups.index(self.group)

        self.HId = []
        self.num_null = []
        self.max_consec_nulls = []
        self.num_points = []
        self.num_zeros = []
        self.max_consec_zeros = []
        # self.time_series = []
        # self.index_series = []

        if not Household.load_data[self.group_num]:
            Household.file_hh[self.group_num] = pd.read_parquet(
                r"C:\Users\corso\OneDrive - University College London"\
                r"\Documents\ERBE CDT\Energy Data Analysis\Data"\
                r"\Working_Data\Matrix\Original\matrix" +
                self.group[0] + '.gzip'
            )
            Household.load_data[self.group_num] = True

        if not AllHouseholds.load_data_all[self.group_num]:
            range_of_households =[
                int(column[2:]) for column in Household.file_hh[Household.groups.index(self.group)].columns]

            for i in tqdm(range_of_households):
                self.HId.append(i)
                self.num_null.append(Household(i).number_of_nulls())
                self.num_points.append(Household(i).number_of_data_points())
                self.num_zeros.append(Household(i).number_of_zeros())
                # self.time_series.append(Household(i).df.dropna().index)
                # self.index_series.append(Household(i).df.reset_index().dropna().index)
                try:
                    self.max_consec_nulls.append(max(Household(i).number_of_consec_nulls(0)))
                except:
                    self.max_consec_nulls.append(0)

                try:
                    self.max_consec_zeros.append(max(Household(i).number_of_consec_zeros(0)))
                except:
                    self.max_consec_zeros.append(0)

            df = pd.DataFrame({'HId': self.HId,
                               'num_null': self.num_null,
                               'consec_nulls': self.max_consec_nulls,
                               'num_points': self.num_points,
                               'num_zeros': self.num_zeros,
                               'consec_zeros': self.max_consec_zeros})
            df = df.loc[df.num_points != 0]
            df['null_percent'] = round(100*df.num_null/(df.num_null+df.num_points), 1)
            df['zeros_percent'] = round(100 * df.num_zeros / df.num_points, 1)
            AllHouseholds.file_all[self.group_num] = df

            AllHouseholds.load_data_all[self.group_num] = True

    def write_or_plot_ah(self, fig, name: 'str', write=False):
        if write == None:
            return fig
        elif write:
            if os.path.exists(r"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"\
                              r"\Energy Data Analysis\Data\Figures\AllHouseholds" + self.group):
                pass
            else:
                os.makedirs(r"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"\
                              r"\Energy Data Analysis\Data\Figures\AllHouseholds" + self.group)

            fig.write_html(r"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"\
                              r"\Energy Data Analysis\Data\Figures\AllHouseholds" +
                           self.group + '/' + name + '.html')
        else:
            fig.show(renderer='browser')

    def hist_of_nulls(self, number_of_bins=50, write=False):
        """Histogram of number of null entries."""
        df = AllHouseholds.file_all[self.group_num]
        fig = px.histogram(df.num_null)
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in
                   np.arange(0, max(df.num_null), round(max(df.num_null) / number_of_bins, -2))]
        )]
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def bar_of_nulls(self, number_of_hh=200, write=False):
        """Bar chart showing the number of null values for each household in descending order.
        'number_of_HH' input represents the top x households that are displayed."""
        df = AllHouseholds.file_all[self.group_num]\
            .sort_values(by='num_null', ascending=False)\
            .reset_index(drop=True)

        fig = px.bar(df, x=df.index, y='num_null', hover_data=['HId', 'null_percent'],
                     labels={'HId': 'Household Id number ', 'num_null': 'Number of null entries ',
                             'consec_nulls': 'Maximum number of consecutive null entries',
                             'null_percent': 'Percentage of null entries', 'x': 'Index'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=slider,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def bar_of_consec_nulls(self, number_of_hh=200, write=False):
        """Bar chart showing the maximum number of consecutive null values for each household in descending order.
                'number_of_HH' input represents the top x households that are displayed."""
        df = AllHouseholds.file_all[self.group_num]\
            .sort_values(by='consec_nulls', ascending=False)\
            .reset_index(drop=True)

        fig = px.bar(df, x=df.index, y='consec_nulls', hover_data=['HId', 'num_null', 'null_percent'],
                     labels={'num_null': 'Number of null entries ', 'HId': 'Household Id number ',
                             'null_percent': 'Percentage of null entries', 'x': 'Index',
                             'consec_nulls': 'Maximum number of consecutive null entries'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=slider,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def bar_of_zeros(self, number_of_hh=200, write=False):
        """Bar chart showing the number of zero entries for each household in descending order.
                'number_of_HH' input represents the top x households that are displayed."""
        df = AllHouseholds.file_all[self.group_num].\
            sort_values(by='num_zeros', ascending=False)\
            .reset_index(drop=True)

        fig = px.bar(df, x=df.index, y='num_zeros', hover_data=['HId', 'zeros_percent'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries', 'x': 'Index'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=slider,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def bar_of_consec_zeros(self, number_of_hh=200, write=False):
        """Bar chart showing the maximum number of consecutive zero entries for each household in descending order.
                        'number_of_HH' input represents the top x households that are displayed."""
        df = AllHouseholds.file_all[self.group_num]\
            .sort_values(by='consec_zeros', ascending=False)\
            .reset_index(drop=True)

        fig = px.bar(df, x=df.index, y='consec_zeros', hover_data=['HId', 'num_zeros', 'zeros_percent'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries', 'x': 'Index',
                             'consec_zeros': 'Maximum number of consecutive zero entries'}
                     )
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=slider,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def bar_of_zeros_percent(self, number_of_hh=200, write=False):
        """Bar chart showing the percentage of zero entries for each household in descending order.
                      'number_of_HH' input represents the top x households that are displayed."""
        df = AllHouseholds.file_all[self.group_num].sort_values(
            by='zeros_percent', ascending=False
        ).reset_index(drop=True)
        fig = px.bar(df, x=df.index, y='zeros_percent', hover_data=['HId', 'num_zeros'],
                     labels={'num_zeros': 'Number of zero entries ', 'HId': 'Household Id number ',
                             'zeros_percent': 'Percentage of zero entries', 'x': 'Index'})
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=slider,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )
        return self.write_or_plot_ah(fig, name=inspect.stack()[0][3], write=write)

    def clean(self, threshold: ['int'], column: ['str']):
        """Function to clean the matrix dataset by excluding data in column x that is greater than some 'threshold'.
        Columns x can relate to any of the following:

        Number of null entries: num_null
        Maximum number of consecutive null entries: consec_nulls
        Number of zero entries: num_zeros
        Maximum number of consecutive zero entries: consec_zeros
        Total number of datapoints (including zeros, excluding NaNs): num_points
        """

        matrix = AllHouseholds.file_all[self.group_num]

        # if there is only one parameter and one threshold to use to clean
        if isinstance(threshold, int) and isinstance(column, str):
            cleaned = self.df.loc[self.df[column] <= threshold]

        # if there are multiple parameters and thresholds to use to clean
        elif isinstance(threshold, list) and isinstance(threshold, list):
            assert len(threshold) == len(column)
            cleaned = self.df.loc[self.df[column[0]] <= threshold[0]]
            for i in range(1, len(column)):
                cleaned = cleaned.loc[cleaned[column[i]] <= threshold[i]]

        # if there are multiple parameters to use to clean by one threshold
        elif isinstance(threshold, int) and isinstance(column, list):
            cleaned = self.df.loc[self.df[column[0]] <= threshold]
            for i in range(1, len(column)):
                cleaned = cleaned.loc[cleaned[column[i]] <= threshold]

        else:
            raise TypeError("Invalid combination of 'columns' and 'thresholds'.")

        hh = ['HH' + str(i) for i in cleaned.HId]
        matrix_clean: object = matrix.loc[:, hh]
        matrix_clean.to_parquet(r"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT"\
                                r"\Energy Data Analysis\Data\Working_Data\Matrix\Originalmatrix" +
                                self.group + '_' +
                                datetime.now().strftime('%H.%M_%d.%m.%Y') + '.gzip'
                                )
        return matrix_clean

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