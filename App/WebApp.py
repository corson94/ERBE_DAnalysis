"""Run this app with `python myApp.py` and
visit http://127.0.0.1:8050/ in your web browser."""

print(f"Loading {__name__} module")

from Model.App.Households.Household import Household
# from Model.App.Households.AllHouseholds import AllHouseholds
from dash import Dash, dcc, html, Input, Output, ctx
import pickle
# from flask import request
# import os
# import pandas as pd
# import plotly.express as px

if 'files' not in locals():
    files = []
    file_names = ['Control', 'ToU', 'HouseholdsC', 'HouseholdsT']
    for file in file_names:
        with open(rf"{Household.directory}\Working_Data\Pickled_objs\{file}.pkl", 'rb') as inp:
            files.append(pickle.load(inp))
    with open(rf"{Household.directory}\Working_Data\Parameters\Pickles\cleaning.pkl", 'rb') as inp:
        params = pickle.load(inp)
else:
    pass

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

graph_height = {'height': '15cm'}

periods = {
    'Half-hourly': 'hh',
    'Daily': 'day',
    'Weekly': 'week',
    'Monthly': 'month'
}

calculations = {
    'Sum': 'sum',
    'Mean': 'mean',
    'Maximum': 'max',
    'Minimum': 'min',
    'None (Half-hourly only)': 'None'
}


def options(label, value):
    return {'label': label, 'value': value}


app = Dash(__name__)

# ------------------------------------------------------------------------------------------------------------------
#                                                   App layout
# ------------------------------------------------------------------------------------------------------------------

app.layout = html.Div([
    # # represents the URL bar, doesn't render anything
    # dcc.Location(id='url', refresh=False),

    html.H1(
        children='Hello ERBE',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H2('Plot showing different metrics for all households'),

    # ----------------------------------------------------------
    #              Graph of metrics for all households

    html.Br(),
    html.Div([
        html.Div([
            html.Label('Group type', style={'display': 'block'}),
            dcc.RadioItems(
                options=[
                    {'label': 'Control group', 'value': 'Control'},
                    {'label': 'Time-of-use group', 'value': 'ToU'}
                ],
                id='group_type',
                value='Control',
                labelStyle={'display': 'block'},
                style={'display': 'block'}
            )],
            style={'display': 'inline-block',
                   'vertical-align': 'top'
                   }
        ),

        # placeholder
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Plot type:', style={'display': 'block'}),
            dcc.Dropdown(
                options=[options(val, key) for key, val in params.items()],
                value='number_of_nulls',
                id='allHousehold_plot_type',
                style={'width': '8cm',
                       'display': 'block'}
            )],
            style={'display': 'inline-block',
                   'vertical-align': 'top'}
        )
        ],
        style={'display': 'flex',
               'align-items': 'center',
               'justify-content': 'center'}
    ),

    dcc.Graph(
        id='allHouseholds_plot',
        style=graph_height),

    html.Br(),

    # --------------------------------------------------------
    #         Graph of metrics for a single household

    html.H2('Plot showing different metrics for a single household'),

    html.Div([
        html.Div([
            html.Label("Household Id (0 - 5565): "),
            dcc.Input(id='household_id', type='number', step=1, min=0, max=5565,
                      style={'display': 'block'},
                      debounce=True)
            ],
            style={'display': 'inline-block',
                   'vertical-align': 'top'}
        ),

        # placeholder
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Plot type:', style={'display': 'block'}),
            dcc.Dropdown(options=[
                {'label': 'Time plot', 'value': 'time_plot'},
                {'label': 'kWh plot', 'value': 'kwh_plot'},
                {'label': 'Frequency plot', 'value': 'frequency_plot'}
            ],
                value='time_plot',
                id='household_plot_type',
                style={'display': 'block',
                       'width': '8cm'}
            )],
            style={'display': 'inline-block',
                   'vertical-align': 'top'}
        ),

        # placeholder
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Period type:', style={'display': 'block'}),
            dcc.Dropdown(options=[options(key, val) for key, val in periods.items()],
                         value='hh',
                         id='household_period_type',
                         style={'display': 'block',
                                'width': '3cm'}
                         )],
            style={'display': 'inline-block',
                   'vertical-align': 'top'}
        ),

        # placeholder
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Calculation type:', style={'display': 'block'}),
            dcc.Dropdown(options=[options(key, val) for key, val in calculations.items()],
                         value='None',
                         id='household_calc_type',
                         style={'display': 'block',
                                'width': '3cm'}
                         )],
            style={'display': 'inline-block',
                   'vertical-align': 'top'}
        )],
        style={'display': 'flex',
               'align-items': 'center',
               'justify-content': 'center'}
    ),

    dcc.Graph(
        id='household_plot',
        style=graph_height),

    # # content will be rendered in this element
    # html.Div(id='page-content')
])

# ------------------------------------------------------------------------------------------------------------------
#                                                   App callback
# ------------------------------------------------------------------------------------------------------------------

# def shutdown():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()

@app.callback(
    Output(component_id='allHouseholds_plot', component_property='figure'),
    Output('household_plot', 'figure'),
    Output('household_id', 'value'),
    # Output('page-content', 'children'),
    Input('group_type', 'value'),
    Input('allHousehold_plot_type', 'value'),
    Input('allHouseholds_plot', 'clickData'),
    Input('household_plot_type', 'value'),
    Input('household_id', 'value'),
    Input('household_period_type', 'value'),
    Input('household_calc_type', 'value'),
    # Input('url', 'pathname')
)
def update_figure(group_type: 'str',
                  allHhousehold_plot_type,
                  click_info,
                  household_plot_type,
                  household_id,
                  period_type,
                  calc):
                  # pathname):
    # if pathname == '/shutdown':
    #     shutdown()
    # else:
    triggered_id = ctx.triggered_id
    print(triggered_id)
    fig_allHh = files[file_names.index(group_type)].bar(allHhousehold_plot_type)
    starting_id = Household.range_of_Households[file_names.index(group_type)][0]

    if triggered_id is None or triggered_id == 'url':
        fig_hh = getattr(files[file_names.index(group_type)+2][int(starting_id)],
                         household_plot_type)(period=period_type, calculation=calc, write=None)
        id_value = starting_id

    elif triggered_id == 'allHouseholds_plot':
        click_hhid = click_info['points'][0]['customdata'][0]
        fig_hh = getattr(files[file_names.index(group_type)+2][int(click_hhid)],
                         household_plot_type)(period=period_type, calculation=calc, write=None)
        id_value = click_hhid

    else:
        fig_hh = getattr(files[file_names.index(group_type)+2][int(household_id)],
                         household_plot_type)(period=period_type, calculation=calc, write=None)
        id_value = household_id

    return fig_allHh, fig_hh, id_value #, html.Div([html.H3(f"You are on page {pathname}")])


app.run_server(debug=True, host='localhost', port=8052)
