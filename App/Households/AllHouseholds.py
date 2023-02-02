import os
import inspect
from tqdm import tqdm
import plotly.express as px
# import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
import pickle

# from Households.Household import Household
from Model.App.Households.Household import Household


def write_new(group: str, param_file_name: str = 'cleaning', name: str = 'cleaning', write_objs=False):
    if Household.file_hh[Household.groups.index(group)] is None:
        Household.file_hh[Household.groups.index(group)] = pd.read_parquet(
            rf"{Household.directory}\Working_Data\Matrix\Different_formats\matrix_ymwd_{group[0]}.gzip")

    range_of_households = [
        int(column[2:]) for column in Household.file_hh[Household.groups.index(group)].columns[4:]]
    if not write_objs:
        with open(rf"{Household.directory}\Working_Data\Parameters\Pickles\{param_file_name}.pkl", 'rb') as inp:
            params = pickle.load(inp)
        df = pd.DataFrame(columns=list(params.keys()), index=range(len(range_of_households)))
        df.insert(loc=0, column='HId', value=[i for i in range_of_households])
        for param in tqdm(params.keys()):
            df[param] = [getattr(Household(i), param)() for i in range_of_households]
        df = df.loc[df.number_of_data_points != 0]
        df.to_parquet(rf"{Household.directory}\Working_Data"
                      rf"\Parameters\Parquets\{name}{group[0]}.gzip")
    else:
        list_objs = [Household(i) for i in range_of_households]
        with open(rf"{Household.directory}\Working_Data\Pickled_objs\Households{group[0]}.pkl", 'wb') as inp:
            pickle.dump(list_objs, inp, -1)


class AllHouseholds():
    """Brings together data from all households within a 'group' by calling on the Household module in order to
    analyse all of them together. Used to determine the extent of the number of NaNs and zeros within the dataset.

    Call in 'AllHouseholds('group') where 'group' can equal either 'Control' or 'ToU'. Then any of the following
    functions can be called to plot the relevant data."""

    # groups = []

    def __init__(self, group: 'str', name: str = 'cleaning'):
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

        # if self.group not in AllHouseholds.groups:
        #     AllHouseholds.groups.append(self.group)
        #     AllHouseholds.groups.sort()
        #     self.group_num = AllHouseholds.groups.index(self.group)

        #     AllHouseholds.file_all[self.group_num] =
        self.file_ = pd.read_parquet(
                f"{Household.directory}\Working_Data\Parameters\Parquets\{name}{self.group[0]}.gzip")
        with open(rf"{Household.directory}\Working_Data\Parameters\Pickles\{name}.pkl", 'rb') as inp:
            self.params = pickle.load(inp)

    def write_or_plot(self, fig, name: 'str', write=False):
        if write is None:
            return fig
        elif write:
            if os.path.exists(rf"{Household.directory}\Figures\AllHouseholds" + self.group):
                pass
            else:
                os.makedirs(rf"{Household.directory}\Figures\AllHouseholds" + self.group)

            fig.write_html(rf"{Household.directory}\Figures\AllHouseholds{self.group}/{name}.html")
        else:
            fig.show(renderer='browser')

    @staticmethod
    def update_fig(fig, number_of_hh):
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=False,
                    range=[0, number_of_hh]
                ),
                type="linear",
                range=[0, round(number_of_hh / 2, 0)]
            )
        )

    def hist_of_nulls(self, number_of_bins=50, write=False):
        """Histogram of number of null entries."""
        df = self.file_
        fig = px.histogram(df.num_null)
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in
                   np.arange(0, max(df.num_null), round(max(df.num_null) / number_of_bins, -2))]
        )]
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)

    def bar(self, y: str, number_of_hh=200, write=None, name=None):
        df = self.file_ \
            .sort_values(by=y, ascending=False) \
            .reset_index(drop=True)
        fig = px.bar(df, x=df.index, y=y, hover_data=self.file_.columns.tolist(),
                     labels={**{'HId': 'Household Id number ', 'x': 'Index'},
                             **self.params})
        AllHouseholds.update_fig(fig, number_of_hh)
        return self.write_or_plot(fig, name=name, write=write)

    def clean(self, threshold: ['int'], column: ['str']):
        """Function to clean the matrix dataset by excluding data in column x that is greater than some 'threshold'.
        Columns x can relate to any of the following:

        Number of null entries: num_null
        Maximum number of consecutive null entries: consec_nulls
        Number of zero entries: num_zeros
        Maximum number of consecutive zero entries: consec_zeros
        Total number of datapoints (including zeros, excluding NaNs): num_points
        """

        matrix = pd.read_parquet(rf"{Household.directory}\Working_Data\Matrix"
                                 rf"\Different_formats\matrix_ymwd_{self.group[0]}.gzip")

        # if there is only one parameter and one threshold to use to clean
        if isinstance(threshold, int) and isinstance(column, str):
            cleaned = self.file_.loc[self.file_[column] <= threshold]

        # if there are multiple parameters and thresholds to use to clean
        elif isinstance(threshold, list) and isinstance(threshold, list):
            assert len(threshold) == len(column)
            cleaned = self.file_.loc[self.file_[column[0]] <= threshold[0]]
            for i in range(1, len(column)):
                cleaned = cleaned.loc[cleaned[column[i]] <= threshold[i]]

        # if there are multiple parameters to use to clean by one threshold
        elif isinstance(threshold, int) and isinstance(column, list):
            cleaned = self.file_.loc[self.file_[column[0]] <= threshold]
            for i in range(1, len(column)):
                cleaned = cleaned.loc[cleaned[column[i]] <= threshold]

        else:
            raise TypeError("Invalid combination of 'columns' and 'thresholds'.")

        hh = ['HH' + str(i) for i in cleaned.HId]
        matrix_clean = matrix.loc[:, hh]
        matrix_clean.to_parquet(rf"{Household.directory}\Working_Data\Matrix\Originalmatrix{self.group}_"
                                rf"{datetime.now().strftime('%H.%M_%d.%m.%Y')}.gzip")
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