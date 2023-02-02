# print(__name__)
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import inspect


class Household:
    """Module that takes the 'matrix' file and returns a df of the chosen household only.
    Then a number of functions can be applied to the household's df to return a range of parameters and plots."""

    directory = r"C:\Users\corso\OneDrive - University College London\Documents" \
                r"\ERBE CDT\Energy Data Analysis\Data"
    groups = ['Control', 'ToU']
    file_hh = [None, None]
    file_number_path = rf"{directory}\Working_Data\Seperated_Files\File_number\Lib\file_number.gzip"
    number_of_Households = pd.read_parquet(file_number_path).LCLid.iloc[-1]
    range_of_Households = [[0, pd.read_parquet(file_number_path).LCLid
                            .loc[pd.read_parquet(file_number_path)['std(0) or ToU(1)'] == 0].iloc[-1] + 1],
                           [pd.read_parquet(file_number_path).LCLid
                            .loc[pd.read_parquet(file_number_path)['std(0) or ToU(1)'] == 0].iloc[-1] + 1,
                            number_of_Households]
                           ]

    def __init__(self, Id):
        """Assign Household to variable using 'LCLid' number as Id."""
        assert isinstance(Id, int)
        assert (Household.range_of_Households[0][0] <= Id <= Household.range_of_Households[1][1])
        self.Id = Id

        if Household.range_of_Households[0][0] <= self.Id < Household.range_of_Households[0][1]:
            self.group = Household.groups[0]
            self.group_num = 0
        else:
            self.group = Household.groups[1]
            self.group_num = 1

        if Household.file_hh[self.group_num] is None:
            Household.file_hh[self.group_num] = pd.read_parquet(rf"{Household.directory}\Working_Data\Matrix"
                                                                rf"\Different_formats\matrix_ymwd_{self.group[0]}.gzip")
        df = Household.file_hh[self.group_num]
        columns = list(df.columns[:4])
        columns.append(f"HH{self.Id}")
        df = df[columns].loc[
             df[f"HH{self.Id}"].first_valid_index():
             df[f"HH{self.Id}"].last_valid_index()]
        df.rename(columns={f"HH{self.Id}": 'kwh'}, inplace=True)
        self.datasets = {'hh_None': df}

    def start_date(self):
        """Returns the timestamp of the first data point for this Household."""
        return self.datasets['hh_None'].index[0]

    def end_date(self):
        """Returns the timestamp of the last data point for this Household."""
        return self.datasets['hh_None'].index[-1]

    def number_of_nulls(self):
        """Returns the number of NaNs for this Household."""
        return self.datasets['hh_None'].isna().sum()

    def nulls_percent(self):
        """Returns the number of NaNs for this Household as a percentage of the total data points."""
        return round(100 * self.datasets['hh_None'].isna().sum() / (self.datasets['hh_None'].isna().sum() + self.datasets['hh_None'].count()), 1)

    def max_number_of_consec_nulls(self, minimum=2):
        """Returns a df with the count of each set of consecutive NaNs, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_nulls = self.datasets['hh_None'].notna().cumsum()[self.datasets['hh_None'].isna()].value_counts().reset_index(drop=True)
        try:
            return max(consec_nulls.loc[consec_nulls >= minimum])
        except ValueError:
            return 0

    def number_of_data_points(self):
        """Returns the number of data points for this Household."""
        return self.datasets['hh_None'].count()

    def number_of_zeros(self):
        """Returns the number of zeros for this Household."""
        return self.datasets['hh_None'].loc[self.datasets['hh_None'] == 0].count()

    def zeros_percent(self):
        """Returns the number of zeros for this Household as a percentage of the total data points."""
        return round(100 * self.datasets['hh_None'].loc[self.datasets['hh_None'] == 0].count() / self.datasets['hh_None'].count(), 1)

    def max_number_of_consec_zeros(self, minimum=2):
        """Returns a df with the count of each set of consecutive zeros, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_zeros = (self.datasets['hh_None'] != 0).cumsum()[self.datasets['hh_None'] == 0].value_counts().reset_index(drop=True)
        try:
            return max(consec_zeros.loc[consec_zeros >= minimum])
        except ValueError:
            return 0

    def agg_data(self, period: str, calculation=None):
        period_format = {
            'day': 'd',
            'week': 'W',
            'month': 'm'
        }
        if period == 'day':
            df_new = getattr(self.datasets['hh_None'].groupby([period]), calculation)()
        elif period != 'year':
            grouped = getattr(self.datasets['hh_None'].groupby(['year', period])["kwh"], calculation)()
            df_new = pd.DataFrame(data=grouped.values,
                                  index=pd.to_datetime([f"{a}-{b}-0" for a, b in grouped.index],
                                                       format=f"%Y-%{period_format[period]}-%w"),
                                  columns=['kwh'])
        self.datasets[f"{period}_{calculation}"] = df_new

    def write_or_plot(self, fig, name: 'str', write=False):
        if write is None:
            return fig
        elif write:
            if os.path.exists(rf"{Household.directory}\Figures\Households\{Household.groups[self.group]}"):
                pass
            else:
                os.makedirs(rf"{Household.directory}\Figures\Households\{Household.groups[self.group]}")

            fig.write_html(rf"{Household.directory}\Figures\Households\{Household.groups[self.group]}\{name}.html")
        else:
            fig.show(renderer='browser')

    def time_plot(self, period='hh', calculation=None, write=False):
        """Returns a plot of time (y-axis) vs data point number (x-axis)."""
        if f"{period}_{calculation}" not in self.datasets:
            self.agg_data(period, calculation)
        df = self.datasets[f"{period}_{calculation}"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df.index, line=dict(color='blue'), name=('H' + str(self.Id))))
        fig.add_trace(go.Scatter(y=pd.date_range(self.start_date(), self.end_date(), freq='30min'),
                                 line=dict(color='red'), name='1:1 plot'))
        fig.update_layout(title=f"{self.number_of_nulls()} null entries out of "
                                f"{self.number_of_data_points() + self.number_of_nulls()}"
                                f"total data points ("
                                f"{round(100 * self.number_of_nulls() / (self.number_of_nulls() + self.number_of_data_points()), 1)} %)")
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)

    def kwh_plot(self, period='hh', calculation=None, write=False):
        """Returns a plot of electricity consumption (kWh) vs time."""
        if f"{period}_{calculation}" not in self.datasets:
            self.agg_data(period, calculation)
        df = self.datasets[f"{period}_{calculation}"]
        fig = px.line(df, x=df.index, y="kwh")
        fig.update_layout(
            xaxis_title_text='Time',
            yaxis_title_text='Electricity consumption (kWh)',
            legend_title_text='Household Id'
        )
        return self.write_or_plot(fig, name=inspect.stack()[0][3], write=write)

    def frequency_plot(self, period: str = 'hh', calculation=None, write=False):
        """Returns a frequency plot of electricity consumption (kWh)."""
        if f"{period}_{calculation}" not in self.datasets:
            self.agg_data(period, calculation)
        df = self.datasets[f"{period}_{calculation}"]
        fig = px.histogram(df.kwh, labels={'variable': 'Household Id',
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
