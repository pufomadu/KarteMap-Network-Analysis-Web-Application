#Import all necessary packages

import dash
from dash_bootstrap_components import themes, Col, Button, FormGroup, Label, Row, Card
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from shortest_path import Dijkstra
from dash.dependencies import Input, Output, State
from geopy.distance import lonlat, distance
from controlsKarteMap import *

#Page design
app = dash.Dash(external_stylesheets=[dbc.themes.SKETCHY], suppress_callback_exceptions=True)


#mapbox token
mapbox_access_token = open(".mapbox_token").read()


#Build map from mapbox using a token
# global fig
fig = go.Figure(go.Scattermapbox(
    mode = "markers+text+lines",
    lon = [], lat =  [],
    marker = {'size': 20, 'symbol': ["airport"]}))

fig.update_layout(
    mapbox = {
        'accesstoken': mapbox_access_token,
        'center': {'lon' : -98.5795, "lat" : 39.0203},
        'style': "outdoors", 'zoom': 3},
    showlegend = False)


#Display information about the source city such as the learn more button, and the images
source_img = dbc.Card(
    [
        dbc.CardBody(html.P(id = "originCity", className="card-text")),
        dbc.Button("Learn More", id = "linkButtonS", color = "warning", external_link = True),
        dbc.CardImg(id = "skylineS", bottom=True),
        dbc.CardImg(id = "stateSealS", bottom=True),

    ],
)

#Display the information about the destination city such as the learn more button, and the images
destination_img = dbc.Card(
    [
        dbc.CardBody(html.P(id = "destinationCity", className="card-text")),
        dbc.Button("Learn More", id = "linkButtonD", color = "warning", external_link = True),
        dbc.CardImg(id = "skylineD", bottom=True),
        dbc.CardImg(id = "stateSealD", bottom=True),
    ],
)

#Build drop down menus
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Start City"),
                dcc.Dropdown(
                    options=[{"label": col, "value": col} for col in finalData['Source_City'].unique()],
                    value="Choose a start city",
                    id="start-city"
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Destination City"),
                dcc.Dropdown(
                    value="Choose a destination city",
                    id="destination-city",
                    options=[{"label": col, "value": col} for col in finalData['Destination_City'].unique()],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Source Airport"),
                dcc.Dropdown(
                    value="sourceAir",
                    id="source-airport"
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Destination Airport"),
                dcc.Dropdown(
                    value="destinationAir",
                    id="destination-airport"
                ),
            ]
        ),
        dbc.Button("Submit", id = "submitButton", outline=True, color="primary", className="mr-1"),
    ],
    body=True,
)

#Build app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1('KarteMap By Precious')
            )
        ),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(
                    dcc.Graph(id="map", figure = fig),
                    width=8),
            ],
            align="center",
        ),

        html.Br(),

        dbc.Row(
            [
                dbc.Col(source_img, width=6),
                dbc.Col(destination_img, md = 6)
            ],
        )

    ],

    id="main-container",
    style={"display": "flex", "flex-direction": "column"},
    fluid=True
)


#Callback and method to display the state seal for the source airport
@app.callback(
    Output("stateSealS", "src"),

    Input('submitButton', 'n_clicks'),

    State('source-airport', 'value'),

)
def update_scr_image(nclicks, srcAir):
    if nclicks:
        return return_seal_url(srcAir)

#Callback and method to display the state skyline for the source airport
@app.callback(
    Output("skylineS", "src"),

    Input('submitButton', 'n_clicks'),

    State('source-airport', 'value'),

)
def update_scr_image(nclicks, srcAir):
    if nclicks:
        return return_skyline_url(srcAir)


# Callback and method to display the state seal for the destination airport
@app.callback(
    Output("stateSealD", "src"),

    Input('submitButton', 'n_clicks'),

    State('destination-airport', 'value'),

)
def update_dest_image(nclicks, destAir):
    if nclicks:
        return return_seal_url(destAir)


# Callback and method to display the state skyline image for the source airport
@app.callback(
    Output("skylineD", "src"),

    Input('submitButton', 'n_clicks'),

    State('destination-airport', 'value'),

)
def update_dest_image(nclicks, destAir):
    if nclicks:
        return return_skyline_url(destAir)


# Callback and method to display the link button for source city.
@app.callback(
    Output("linkButtonS", "href"),

    Input('submitButton', 'n_clicks'),

    State('source-airport', 'value'),
)
def update_src_link(nclicks, srcAir):
    if nclicks:
        state = return_state(srcAir)
        url = images_df.loc[images_df['state'] == state, "capital_url"].values[0]
        return url


# Callback and method to display the link button for destination city.
@app.callback(
    Output("linkButtonD", "href"),

    Input('submitButton', 'n_clicks'),

    State('destination-airport', 'value'),
)
def update_src_link(nclicks, destAir):
    if nclicks:
        state = return_state(destAir)
        url = images_df.loc[images_df['state'] == state, "capital_url"].values[0]
        return url

# Callback to display the State name and population for source city.
@app.callback(
    Output("originCity", "children"),

    Input('submitButton', 'n_clicks'),

    State('source-airport', 'value'),
)
def display_src_info(nclicks, srcAir):

    if nclicks:
        city = finalData.loc[finalData['Source_Airport'] == srcAir, "Source_City"].values[0]
        population = city_df.loc[city_df['City'] == city, "Population"].values[0]
        return f"The population in {city} is {population}."


# Callback and method to display the State name and population for the destination city.
@app.callback(
    Output("destinationCity", "children"),

    Input('submitButton', 'n_clicks'),

    State('destination-airport', 'value'),
)
def display_dest_info(nclicks, destAir):

    if nclicks:
        city = finalData.loc[finalData['Source_Airport'] == destAir, "Source_City"].values[0]
        population = city_df.loc[city_df['City'] == city, "Population"].values[0]
        return f"The population in {city} is {population}."


# callback and method to update the source airport dropdown menu based on the selected city
@app.callback(
    dash.dependencies.Output("source-airport", "options"),
    Input(component_id='start-city', component_property='value'),
)
def update_Source_options(search_value):
    x = finalData[finalData["Source_City"] == search_value]
    return [{"label": col, "value": col} for col in x['Source_Airport'].unique()]

#callback and method to update the destination airport dropdown menu based on the selected city
@app.callback(
    dash.dependencies.Output("destination-airport", "options"),
    Input(component_id='destination-city', component_property='value'),
)
def update_Destination_options(search_value):
    x=finalData[finalData["Destination_City"]==search_value]
    return [{"label": col, "value": col} for col in x['Destination_Airport'].unique()]


#Callback and method to display the map and
@app.callback(
    Output('map', 'figure'),
    Input('submitButton', 'n_clicks'),
    [
        State('source-airport', 'value'),
        State('destination-airport', 'value'),
    ],
)
def display_graph(n_clicks, sourceA, stopA, fig=fig):

    if n_clicks:
        apt_lat = []
        apt_lon = []

        network = buildNet()
        Dijkstra.compute(network, network.get_node(sourceA))
        path_shortest = []

        # show the shortest path(s) from start airport to stop airport
        nw_dest = network.get_node(stopA)
        path_shortest = [nw_dest.get_name()]
        Dijkstra.compute_shortest_path(nw_dest, path_shortest)

        # get LongLat of airport in path
        for apt in path_shortest[::-1]:
            apt_df_row = finalData.loc[finalData['Source_Airport'] == apt]
            apt_lat.append(apt_df_row["Source_Latitude"].unique()[0])
            apt_lon.append(apt_df_row["Source_Longitude"].unique()[0])


        fig = go.Figure(go.Scattermapbox(
            mode="markers+text+lines",
            lon= apt_lon,
            lat= apt_lat,
            marker={'size': 20, 'symbol': ["airport"]}))


        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox={
                'accesstoken': mapbox_access_token,
                'center':  {'lon' : -98.5795, "lat" : 39.0203},
                'style': "outdoors", 'zoom': 4,
            }
        )
    #return updated graph
    return fig;



#Main
if __name__ == "__main__":
    app.run_server(debug=True)