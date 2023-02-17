import os
import math
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px


def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def rounddown(x):
    return int(math.floor(x / 10.0)) * 10


def visulization(df):
    """
    Based on the dataframe do visulization using dash.
    :param df: processed data
    :return: app: dash app
    """
    date_time = '2021-01-18'
    qtrs = ["2019Q3", "2019Q4", "2020Q1", "2020Q2", "2020Q3", "2020Q4"]
    aspects = {'Personal_Income_Change': "Personal income change",
               'UnemploymentRate(%)': "Unemployment",
               'GDP_growth_rate': "GDP growth",
               'CFR': 'case fatality ratio (CFR)'
               }
    df['text'] = '<b>' + df['State'] + '</b>' + '<br>' + \
                 'Mask Mandate: ' + df['Mask'] + '<br>' + \
                 '<b>' + date_time + ":" + '</b>' + '<br>' + \
                 'Cases: ' + df['Cases_p'].astype(str) + '<br>' + \
                 'Deaths: ' + df['Deaths_p'].astype(str) + '<br>'

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    server = app.server

    # App layout
    colors = {
        'background': '#ffffff',
        'background_h': '#e7e5e4',
        'text': '#f2420d',
        'text_1': '#863921',
    }

    app.layout = html.Div(children=[
        html.H1("How Covid-19 epidemic affect the U.S. economy?",
                style={'text-align': 'center',
                       'color': colors['text']
                       }
                ),
        dcc.Dropdown(id="slct_period",
                     options=[
                         {"label": "2019Q3", "value": "2019Q3"},  # lable: what users see
                         {"label": "2019Q4", "value": "2019Q4"},
                         {"label": "2020Q1", "value": "2020Q1"},
                         {"label": "2020Q2", "value": "2020Q2"},
                         {"label": "2020Q3", "value": "2020Q3"},
                         {"label": "2020Q4", "value": "2020Q4"},
                         {"label": "2021Q1-p", "value": "2021Q1"}, ],
                     placeholder="Select a time period (quarter)",
                     multi=False,
                     style={'width': "50%",
                            'text-align': 'center',
                            'margin': '10 50 10'
                            }
                     ),
        dcc.RadioItems(id="slct_aspect",
                       options=[
                           {'label': 'case fatality ratio (CFR)', 'value': 'CFR'},
                           {'label': 'Unemployment', 'value': 'UnemploymentRate(%)'},
                           {'label': 'Personal Income Change', 'value': 'Personal_Income_Change'},
                           {'label': 'GDP Growth', 'value': 'GDP_growth_rate'},
                       ],
                       value='UnemploymentRate(%)',  # default
                       labelStyle={'display': 'inline-block'}
                       ),

        html.Div(id='output_container', children=[], style={'color': colors['text']}),
        html.Br(),
        dcc.Graph(id='my_map', figure={}, style=dict(width='100%')),
    ],
        style={'backgroundColor': colors['background_h'],
               "width": "80%",
               'display': 'blocl', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw',
               },
    )

    @app.callback(
        [Output(component_id='output_container', component_property='children'),
         Output(component_id='my_map', component_property='figure')],  # graph: map
        [Input(component_id='slct_period', component_property='value'),
         Input(component_id='slct_aspect', component_property='value')
         ]
    )
    def update_graph(option_slctd_dropdown, option_slctd_radioitem):
        dff = df.copy()
        dff = dff[dff["Qtr"] == option_slctd_dropdown][['Qtr', 'StateAbbreviation', option_slctd_radioitem]]

        container = "The chosen time period was: {}; ".format(
            option_slctd_dropdown) + "The chosen aspect was: {}.".format(
            aspects[option_slctd_radioitem])

        # Plotly Graph Objects (GO)
        fig = go.Figure(
            data=[go.Choropleth(
                locationmode='USA-states',
                locations=dff['StateAbbreviation'],
                z=dff[option_slctd_radioitem].astype(float),
                colorscale='RdYlGn',  # Reds, RdYlGn, Picnic, RdGy
                zmin=rounddown(df[[option_slctd_radioitem]].min()),
                zmax=roundup(df[[option_slctd_radioitem]].max()),
                colorbar=dict(
                    title='% ' + aspects[option_slctd_radioitem],
                    thickness=40, thicknessmode='pixels',
                    ticks="outside",
                ),
                text=df['text'],
                marker_line_color='white',  # line markers between states
            )]
        )
        fig.update_layout(
            # title
            title_text=aspects[option_slctd_radioitem] + " rate (%)" + " in the USA",
            title_xanchor="center",
            title_font=dict(size=20),
            title_x=0.5,
            # hover
            # hoverlabel=dict(
            # bgcolor="white",
            # font_size=12,
            # font_family="Rockwell"),
            # map
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=True,  # lakes
                lakecolor='rgb(255, 255, 255)'),
            # color
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
        )

        return container, fig

    return app
