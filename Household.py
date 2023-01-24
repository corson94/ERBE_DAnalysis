import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class Household:
    """Help is on its way"""
    load_dataC = False
    load_dataT = False
    fileC = pd.DataFrame()
    fileT = pd.DataFrame()
    file_number = pd.read_parquet('Data/Working_Data/Seperated_Files/File_number/Lib/file_number.gzip')
    number_of_Households = file_number.LCLid.iloc[-1]
    range_of_CHouseholds = [0, file_number.LCLid.loc[file_number['std(0) or ToU(1)'] == 0].iloc[-1]+1]
    range_of_THouseholds = [range_of_CHouseholds, number_of_Households+1]

    def __init__(self, Id):
        """Assign Household to variable using 'LCLid' number as Id."""
        assert(0 <= Id <= 5565)
        self.Id = Id
        if 0 <= self.Id < 4443:
            if not Household.load_dataC:
                file = pd.read_parquet('Data/Working_Data/Matrix/matrixC.gzip')
                Household.load_dataC = True
                Household.fileC = file
            dataframe = Household.fileC['HH' + str(self.Id)].loc[
                        Household.fileC['HH' + str(self.Id)].first_valid_index():
                        Household.fileC['HH' + str(self.Id)].last_valid_index()]
            self.dataframe = dataframe

        elif 4442 < self.Id < 5566:
            if not Household.load_dataT:
                file = pd.read_parquet('Data/Working_Data/Matrix/matrixT.gzip')
                Household.load_dataT = True
                Household.fileT = file
            dataframe = Household.fileT['HH' + str(self.Id)].loc[
                        Household.fileT['HH' + str(self.Id)].first_valid_index():
                        Household.fileT['HH' + str(self.Id)].last_valid_index()]
            self.dataframe = dataframe

    def start_date(self):
        """Returns the timestamp of the first data point for this Household."""
        return self.dataframe.index[0]

    def end_date(self):
        """Returns the timestamp of the last data point for this Household."""
        return self.dataframe.index[-1]

    def number_of_nulls(self):
        """Returns the number of NaNs for this Household."""
        return self.dataframe.isna().sum()

    def number_of_consec_nulls(self, minimum = 2):
        """Returns a dataframe with the count of each set of consecutive NaNs, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_nulls = self.dataframe.notna().cumsum()[self.dataframe.isna()].value_counts().reset_index(drop=True)
        return consec_nulls.loc[consec_nulls >= minimum]

    def number_of_data_points(self):
        """Returns the number of data points for this Household."""
        return self.dataframe.count()

    def number_of_zeros(self):
        """Returns the number of zeros for this Household."""
        return self.dataframe.loc[self.dataframe == 0].count()

    def number_of_consec_zeros(self, minimum = 2):
        """Returns a dataframe with the count of each set of consecutive zeros, starting from sets of x where x is
        defined by the 'minimum' input"""
        consec_zeros = (self.dataframe != 0).cumsum()[self.dataframe == 0].value_counts().reset_index(drop=True)
        return consec_zeros.loc[consec_zeros >= minimum]

    def time_plot(self):
        """Returns a plot of time (y-axis) vs data point number (x-axis)."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=self.dataframe.dropna().index,line=dict(color='blue'), name=('H'+str(self.Id))))
        fig.add_trace(go.Scatter(y=pd.date_range(self.start_date(), self.end_date(), freq='30min'),
                                 line=dict(color='red'), name='1:1 plot'))
        fig.update_layout(title= (str(self.number_of_nulls()) +
                                  ' null entries out of ' +
                                  str(self.number_of_data_points() +
                                      self.number_of_nulls()) +
                                  ' total data points (' +
                                  str(round(100*self.number_of_nulls()/(self.number_of_nulls()+self.number_of_data_points()),1)) +
                                  '%)')
                          )
        fig.show(renderer='browser')
        return fig

    def kwh_plot(self):
        """Returns a plot of electricity consumption (kWh) vs time."""
        fig = px.line(self.dataframe)
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        fig.show(renderer='browser')
        return fig

    def frequency_plot(self):
        """Returns a frequency plot of electricity consumption (kWh)."""
        fig = px.histogram(self.dataframe, labels={'variable': 'Household Id',
                                                   'count': 'Frequency',
                                                   'value': 'Electricity consumption (kWh)'})
        fig.layout.sliders = [dict(
            active=4,
            currentvalue={"prefix": "Bin size: "},
            pad={"t": 20},
            steps=[dict(label=i, method='restyle', args=['xbins.size', i]) for i in np.linspace(0, 0.2, 21)]
            )]
        fig.update_layout(xaxis_title_text='Electricity consumption (kWh)',
                          yaxis_title_text= 'Frequency',
                          legend_title_text= 'Household Id')
        fig.show(renderer='browser')
        return fig
