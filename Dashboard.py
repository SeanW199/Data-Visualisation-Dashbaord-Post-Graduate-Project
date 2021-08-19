# imports the relevant dashboard, data visualisation and dataframe libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# gets the datasets URL and sets them as relevant variables
confirmedDatasetURL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
deathsDatasetURL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
recoveredDatasetURL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

# sets the URL variables as pandas data frames
confirmed = pd.read_csv(confirmedDatasetURL)
deaths = pd.read_csv(deathsDatasetURL)
recovered = pd.read_csv(recoveredDatasetURL)

# unpivot data frames and updating the datasets to have one single date column
dateOne = confirmed.columns[4:]
confirmed = confirmed.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=dateOne,
                           var_name='date', value_name='confirmed')
dateTwo = deaths.columns[4:]
deaths = deaths.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=dateTwo, var_name='date',
                     value_name='deaths')
dateThree = recovered.columns[4:]
recovered = recovered.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=dateThree,
                           var_name='date', value_name='recovered')

# # lowering the size in memory of the dataset to complete prep due to memory constraints
confirmed['Lat'] = confirmed['Lat'].astype('float32')
confirmed['Long'] = confirmed['Long'].astype('float32')
confirmed['confirmed'] = confirmed['confirmed'].astype('int32')

deaths['Lat'] = deaths['Lat'].astype('float32')
deaths['Long'] = deaths['Long'].astype('float32')
deaths['deaths'] = deaths['deaths'].astype('int32')

recovered['Lat'] = recovered['Lat'].astype('float32')
recovered['Long'] = recovered['Long'].astype('float32')
recovered['recovered'] = recovered['recovered'].astype('int32')

# merging the datasets into one
completeCovid_19Dataset = confirmed.merge(right=deaths,
                                          how='left',
                                          on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])

completeCovid_19Dataset = completeCovid_19Dataset.merge(right=recovered,
                                                        how='left',
                                                        on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])

# setting the date to the correct format format
completeCovid_19Dataset['date'] = pd.to_datetime(completeCovid_19Dataset['date'])

# reset all N/A values to 0 in the recovered column
completeCovid_19Dataset['recovered'] = completeCovid_19Dataset['recovered'].fillna(0)

# calculates current active cases of covid-19
completeCovid_19Dataset['active'] = completeCovid_19Dataset['confirmed'] - completeCovid_19Dataset['deaths'] - \
                                    completeCovid_19Dataset['recovered']

# creates a backup dataset to be used in the call backs
backupDataSet = completeCovid_19Dataset

# creating 2 new sub data sets based on statistics around date and the country.
covid_19SubDataset_DCDRA = completeCovid_19Dataset.groupby(['date'])[
    ['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()

completeCovid_19Dataset = completeCovid_19Dataset.groupby(['date', 'Country/Region'])[
    ['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()

covid_19SubDataset_DCDRA['recovered'] = covid_19SubDataset_DCDRA['recovered'].astype('int32')

covid_19SubDataset_DCDRA['active'] = covid_19SubDataset_DCDRA['active'].astype('int32')

# Gets the header value from the dataframe and puts them to a list
headers = list(completeCovid_19Dataset.columns.values.tolist()[-4:])


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# This function loads in the world map visualisation at the top of the dashboard.
def world_map():
    newData = backupDataSet
    fig = px.scatter_geo(newData,
                         lat=newData['Lat'],
                         lon=newData['Long'],
                         color="Country/Region",
                         hover_name='Country/Region',
                         hover_data=['Province/State'],
                         size='deaths',
                         )
    fig.update_layout(template="plotly_dark")
    return fig
    # fig = px.scatter_mapbox() Do not use


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# setting up the Dash app dashboard
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# this line creates the app layout using a dash container
app.layout = dbc.Container([

    # this line creates the help box at the top right of the dashboard and contains a string instructing the user how
    # to use the dashboard.
    dbc.Row(children=[
        dbc.Col([
            dbc.Button("Help?",
                       className="float-right",
                       size="sm",
                       outline=False,
                       color="secondary",
                       id="popoverButton",
                       ),

            dbc.Popover([dbc.PopoverHeader("Help"),
                         dbc.PopoverBody(
                             "This page is to help You understand how to use this Covid-19 Dashboard. The first graph at the top of the dashboard is an interactive world map, where the user can hover over a country and view their current Covid-19 death statistics. The values after that show the total global deaths, recoveries, active and confirmed cases for covid-19. The second section of the dashboard allows the user to select a country from the dropdown on the left side. This will change the line and bar chart. It will also change the statistics for that country and title which will make you aware of your change. The final and bottom section of the dashboards will allow the user to create your own graph comparing countries. This is done through the first two dropdown boxes which will set X1 and X2 in the graph the third dropdown box will allow you to pick the Y of the graph choosing form death, confirmed , active or recovered cases. This will then create a graph that you can create. For all of these graphs if you hover over them the are options at the top right which the user may select these options to view all the data at the point of their mouse while hovering on the graph or zoom in to a specific section the user can highlight just to view that data  Click on the help box again to close this tab."
                         )],
                        id="popover",
                        target="popoverButton",
                        placement="bottom",
                        is_open=False),
        ])
    ]),

    # this is creating the title text and centers it to the center of the dashboard
    dbc.Row(children=[dbc.Col(html.H1('Covid-19 Dashboard', className='text-center pb-2'), width=12),
                      ], no_gutters=False),

    # this creates creates a graph element of the world map that shows relevant stats based on the function above
    dbc.Row([
        dbc.Col(dcc.Graph(figure=world_map()), className='badge-dark p-2'),
    ]),

    # this section of code formats the total values of deaths, recoveries, confirmed and active covid cases and gets
    # their totals from the dataframe
    dbc.Row(
        [dbc.Col(children=[html.H6("Total Confirmed Covid-19 Cases"),
                           html.H5(str("{:,}".format(covid_19SubDataset_DCDRA['confirmed'].max())))],
                 className="badge badge-secondary px-2 pb-2", width=3),
         dbc.Col(children=[html.H6("Total Recovered Covid-19 Cases"),
                           html.H5(str("{:,}".format(covid_19SubDataset_DCDRA['recovered'].max())))],
                 className="badge badge-success px-2 pb-2", width=3),
         dbc.Col(children=[html.H6("Total Deaths Due To Covid-19"),
                           html.H5(str("{:,}".format(covid_19SubDataset_DCDRA['deaths'].max())))],
                 className="badge badge-danger px-2 pb-2", width=3),
         dbc.Col(children=[html.H6("Total Active Covid-19 Cases"),
                           html.H5(str("{:,}".format(covid_19SubDataset_DCDRA['active'].max())))],
                 className="badge badge-warning px-2 pb-2", width=3),
         ], ),

    # this section of code sets up the dropdown box for users to select the county they wish to view the stats on.
    dbc.Row([
        dbc.Col([dcc.Dropdown(id='countryDropdown1',
                              className='badge-dark text-dark py-2',
                              multi=False,
                              value='United Kingdom',
                              options=[{'label': x, 'value': x}
                                       for x in sorted(completeCovid_19Dataset['Country/Region'].unique())],
                              placeholder='Please select a country',
                              clearable=False, ),

                 dcc.Graph(id='line-chart',
                           figure={},
                           className="pt-2")
                 ], className="badge-dark", width=6),

        # this piece of code sets up the title so the user can see what country they have selected.
        dbc.Col(children=[html.H5(id='Country_label',
                                  children=[], className="badge-dark"),

                          dcc.Graph(id='pie_chart',
                                    figure={})
                          ], className="badge-dark pt-2", width=3),

        # this section of code sets up the area for daily covid data will be displayed to the user based on the
        # country tey have selected
        dbc.Col(children=[html.H4("Covid-19 Statistics"),
                          html.H6('New confirmed Covid-19 Cases', className="pt-2"),
                          html.H5(id='new_confirmed', children=[]),
                          html.H6('New daily % for confirmed cases'),
                          html.H6(id='NC%Increase', children=[]),
                          html.H6('New recoveries Covid-19 Cases', className="pt-2"),
                          html.H5(id='new_recovered', children=[]),
                          html.H6('New daily % for recovered cases'),
                          html.H6(id='NR%Increase', children=[]),
                          html.H6('New deaths due to Covid-19 Cases', className="pt-2"),
                          html.H5(id='new_deaths', children=[]),
                          html.H6('New daily % for deaths cases'),
                          html.H6(id='ND%Increase', children=[]),
                          html.H6('New active Covid-19 Cases', className="pt-2"),
                          html.H5(id='new_active', children=[]),
                          html.H6('New daily % for active cases'),
                          html.H6(id='NA%Increase', children=[]),
                          ], className="badge badge-secondary pt-2", width=3),
    ], no_gutters=False),

    # sets the title for the next section
    dbc.Row([
        dbc.Col([html.H2("Country Comparison Tool")], className='badge-dark text-center', width=12)
    ], no_gutters=False),

    # this section of code created the 2 drop down boxes  for the user to select for the comparison graph X1, X2.
    dbc.Row([
        dbc.Col([dcc.Dropdown(id='countryDropdown2',
                              multi=False, value='United Kingdom',
                              options=[{'label': x, 'value': x}
                                       for x in sorted(completeCovid_19Dataset['Country/Region'].unique())],
                              placeholder='Please select a country',
                              clearable=False, )], className='badge-dark text-dark py-2', ),

        dbc.Col([dcc.Dropdown(id='countryDropdown3',

                              multi=False, value='France',
                              options=[{'label': x, 'value': x}
                                       for x in sorted(completeCovid_19Dataset['Country/Region'].unique())],
                              placeholder='Please select a country',
                              clearable=False, )], className='badge-dark text-dark py-2', ),
    ], no_gutters=False),

    # this section sets up the dropdown box for the user to select the category they would like to select for the
    # comparison graph, Y
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='catDropdown',
                         multi=False, value='confirmed',
                         options=[{'label': x, 'value': x}
                                  for x in headers],
                         placeholder='Please select a category',
                         clearable=False, )], className='badge-dark text-dark py-2', width=12),

    ], no_gutters=False),

    # this section of code sets up the area for a graph to be palced
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart',
                      figure={})
        ], className="badge-dark pb-2", width=12)

    ]),

    # this section of code sets up the external link to a website that holds the covid-19 polices for most of the
    # countries in hte world.
    dbc.Row([dbc.Col([
        html.Label(['Link to individual countries Covid-19 polices: ',
                    html.A('Link',
                           href='https://www.ilo.org/global/topics/coronavirus/regional-country/country-responses/lang--en/index.htm#GB')])
    ], className='badge-dark'),
    ]),
    # closes the layout container and sets fulid to false which creates the 2 line boarders at the sides of the dashabord
], fluid=False)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# this creates a dynamic callback to open and close the help button when it is clicked
@app.callback(
    Output("popover", "is_open"),
    [Input("popoverButton", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


# this creates a dynamic callback to create the line chart graph based on the country selected from a drop down box
@app.callback(
    Output("line-chart", "figure"),
    [Input("countryDropdown1", "value")])
def update_line_chart(countrySelected):
    mask = completeCovid_19Dataset['Country/Region'] == countrySelected
    fig = px.line(completeCovid_19Dataset[mask],
                  x="date", y=["deaths", "recovered", "active", "confirmed"],
                  color_discrete_sequence=['red', 'green', 'orange', 'grey'],
                  title='Covid-19 overtime from 2020-2021')
    fig.update_layout(template="plotly_dark")
    return fig


# this creates a dynamic callback to create a title based on the country selected
@app.callback(
    Output("Country_label", "children"),
    [Input("countryDropdown1", "value")])
def update_cTitle(countrySelected1):
    container = 'Covid-19 Stats for: {}'.format(countrySelected1)
    return container


# this creates a dynamic callback to create a pie chart based on the country selected
@app.callback(
    Output('pie_chart', 'figure'),
    [Input("countryDropdown1", "value")])
def update_pie_chart(countrySelected2):
    newData = completeCovid_19Dataset
    new_confirmed = newData[newData['Country/Region'] == countrySelected2]['confirmed'].iloc[-1]
    new_deaths = newData[newData['Country/Region'] == countrySelected2]['deaths'].iloc[-1]
    new_active = newData[newData['Country/Region'] == countrySelected2]['active'].iloc[-1]
    new_recovered = newData[newData['Country/Region'] == countrySelected2]['recovered'].iloc[-1]

    fig = px.pie(
        data_frame=newData,
        values=[new_deaths, new_recovered, new_active, new_confirmed],
        names=["deaths", "recovered", "active", "confirmed"],
        color=["deaths", "recovered", "active", "confirmed"],
        color_discrete_sequence=['red', 'green', 'orange', 'grey'],
        hole=.3,
        title='Covid-19 Date Percentages',

    )
    fig.update_layout(template="plotly_dark")
    return fig


# this creates a dynamic callback to create a stats based on the country selected
@app.callback(
    Output('new_confirmed', 'children'),
    Output('NC%Increase', 'children'),
    Output('new_recovered', 'children'),
    Output('NR%Increase', 'children'),
    Output('new_deaths', 'children'),
    Output('ND%Increase', 'children'),
    Output('new_active', 'children'),
    Output('NA%Increase', 'children'),
    [Input("countryDropdown1", "value")]
)
def update_stats(dropdown1):
    newData = completeCovid_19Dataset
    newData = newData[newData['Country/Region'] == dropdown1]

    new_confirmed = newData['confirmed'].iloc[-1] - newData['confirmed'].iloc[-2]
    percentageIncreaseNC = ((new_confirmed / newData['confirmed'].iloc[-1]) * 100)

    new_recovered = newData['recovered'].iloc[-1] - newData['recovered'].iloc[-2]
    percentageIncreaseNR = ((new_recovered / newData['recovered'].iloc[-1]) * 100)

    new_deaths = newData['deaths'].iloc[-1] - newData['deaths'].iloc[-2]
    percentageIncreaseND = ((new_deaths / newData['deaths'].iloc[-1]) * 100)

    new_active = newData['active'].iloc[-1] - newData['active'].iloc[-2]
    percentageIncreaseNA = ((new_active / newData['active'].iloc[-1]) * 100)

    container = ['{}'.format(str(new_confirmed)),
                 str('{:.2f}'.format(percentageIncreaseNC) + '%'),
                 '{}'.format(str(new_recovered.astype('int32'))),
                 str('{:.2f}'.format(percentageIncreaseNR) + '%'),
                 '{}'.format(str(new_deaths)),
                 str('{:.2f}'.format(percentageIncreaseND) + '%'),
                 '{}'.format(str(new_active.astype('int32'))),
                 str('{:.2f}'.format(percentageIncreaseNA) + '%'),
                 ]
    return container


# this creates a dynamic callback to create a bar chart based on the 2 countries selected and the category selected
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('countryDropdown2', 'value'),
     Input('countryDropdown3', 'value'),
     Input('catDropdown', 'value')]
)
def comparisonGraph(dropdown1, dropdown2, catDropdown):
    newData = completeCovid_19Dataset
    country1 = newData[newData['Country/Region'] == dropdown1]
    country2 = newData[newData['Country/Region'] == dropdown2]
    Dataset = pd.concat([country1, country2], axis=0)
    fig = px.bar(Dataset,
                 x='Country/Region',
                 y=catDropdown,
                 color='Country/Region'
                 )
    fig.update_layout(template="plotly_dark")
    return fig


# this runs the code above
if __name__ == "__main__":
    app.run_server(debug=False)
