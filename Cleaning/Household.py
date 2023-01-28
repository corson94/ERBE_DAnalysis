import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import inspect


class Household:
    """Module that takes the 'matrix' file and returns a df of the chosen household only.
    Then a number of functions can be applied to the household's df to return a range of parameters and plots."""

    groups = ['Control', 'ToU']
    file_hh = [(), ()]
    load_data = [False, False]
    file_number = pd.read_parquet(r"C:\Users\corso\OneDrive - University College London\Documents\ERBE CDT" \
                                  r"\Energy Data Analysis\Data\Working_Data\Seperated_Files\File_number\Lib" \
                                  r"\file_number.gzip")

    number_of_Households = file_number.LCLid.iloc[-1]
    range_of_Households = [[0, file_number.LCLid.loc[file_number['std(0) or ToU(1)'] == 0].iloc[-1] + 1],
                           [file_number.LCLid.loc[file_number['std(0) or ToU(1)'] == 0].iloc[-1] + 1,
                            number_of_Households]
                           ]

    def __init__(self, Id):
        """Assign Household to variable using 'LCLid' number as Id."""
        assert isinstance(Id, int)
        assert (0 <= Id <= 5565)
        self.Id = Id

        if Household.range_of_Households[0][0] <= self.Id < Household.range_of_Households[0][1]:
            self.group = Household.groups[0]
            self.group_num = 0
        else:
            self.group = Household.groups[1]
            self.group_num = 1

        if not Household.load_data[self.group_num]:
            Household.file_hh[self.group_num] = pd.read_parquet(r"C:\Users\corso\OneDrive - University College London"\
                                                         r"\Documents\ERBE CDT\Energy Data Analysis\Data"\
                                                         r"\Working_Data\Matrix\Original\matrix" +
                                                         self.group[0] + '.gzip')

            Household.load_data[self.group_num] = True

        df = Household.file_hh[self.group_num]['HH' + str(self.Id)].loc[
                    Household.file_hh[self.group_num]['HH' + str(self.Id)].first_valid_index():
                    Household.file_hh[self.group_num]['HH' + str(self.Id)].last_valid_index()]
        self.df = df

    def start_date(self):
        """Returns the timestamp of the first data point for this Household."""
        return self.df.index[0]

    def end_date(self):
        """Returns the timestamp of the last data point for this Household."""
        return self.df.index[-1]

    def number_of_nulls(self):
        """Returns the number of NaNs for this Household."""
        return self.df.isna().sum()

    def number_of_consec_nulls(self, minimum=2):
        """Returns a df with the count of each set of consecutive NaNs, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_nulls = self.df.notna().cumsum()[self.df.isna()].value_counts().reset_index(drop=True)
        return consec_nulls.loc[consec_nulls >= minimum]

    def number_of_data_points(self):
        """Returns the number of data points for this Household."""
        return self.df.count()

    def number_of_zeros(self):
        """Returns the number of zeros for this Household."""
        return self.df.loc[self.df == 0].count()

    def number_of_consec_zeros(self, minimum=2):
        """Returns a df with the count of each set of consecutive zeros, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_zeros = (self.df != 0).cumsum()[self.df == 0].value_counts().reset_index(drop=True)
        return consec_zeros.loc[consec_zeros >= minimum]

    def write_or_plot(self, fig, name: 'str', write=False):
        if write == None:
            return fig
        elif write:
            if os.path.exists('Data/Figures/Households/' + Household.groups[self.group]):
                pass
            else:
                os.makedirs('Data/Figures/Households/' + Household.groups[self.group])

            fig.write_html('Data/Figures/Households/' + Household.groups[self.group] + '/' + name + '.html')
        else:
            fig.show(renderer='browser')

    def time_plot(self, write=False):
        """Returns a plot of time (y-axis) vs data point number (x-axis)."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=self.df.dropna().index, line=dict(color='blue'), name=('H' + str(self.Id))))
        fig.add_trace(go.Scatter(y=pd.date_range(self.start_date(), self.end_date(), freq='30min'),
                                 line=dict(color='red'), name='1:1 plot'))
        fig.update_layout(title=(str(self.number_of_nulls()) +
                                 ' null entries out of ' +
                                 str(self.number_of_data_points() +
                                     self.number_of_nulls()) +
                                 ' total data points (' +
                                 str(round(100 * self.number_of_nulls() / (
                                             self.number_of_nulls() + self.number_of_data_points()), 1)) +
                                 '%)')
                          )
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)

    def kwh_plot(self, write=False):
        """Returns a plot of electricity consumption (kWh) vs time."""
        fig = px.line(self.df)
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)

    def frequency_plot(self, write=False):
        """Returns a frequency plot of electricity consumption (kWh)."""
        fig = px.histogram(self.df, labels={'variable': 'Household Id',
                                                   'count': 'Frequency',
                                                   'value': 'Electricity consumption (kWh)'})
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in np.linspace(0, 0.2, 21)]
        )]
        fig.update_layout(xaxis_title_text='Electricity consumption (kWh)',
                          yaxis_title_text='Frequency',
                          legend_title_text='Household Id')
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)
