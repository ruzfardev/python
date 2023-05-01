# Import packages
from dash import Dash, dcc, Output, Input, State
import dash_mantine_components as dmc
import requests
import geopy
from geopy.geocoders import Nominatim
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify
import requests

geolocator = Nominatim(user_agent="my_app")


external_stylesheets_dmc = [dmc.theme.DEFAULT_COLORS]
# Initialize the app

app = Dash(__name__, external_stylesheets=external_stylesheets_dmc)

df_airports = pd.DataFrame({
    'airport': ['JFK', 'LGA', 'SFO', 'ORD', 'LAX'],
    'city': ['New York', 'New York', 'San Francisco', 'Chicago', 'Los Angeles'],
    'state': ['NY', 'NY', 'CA', 'IL', 'CA'],
    'cnt': [100, 50, 75, 60, 90],
    'lat': [40.639751, 40.777245, 37.618972, 41.974162, 33.942536],
    'long': [-73.778925, -73.872608, -122.374889, -87.907321, -118.408074]
})
#
# # create figure with plotly express
fig = px.scatter_geo(
    df_airports,
    locationmode="USA-states",
    lat="lat",
    lon="long",
    hover_data=["airport", "city", "state", "cnt"],
    color="cnt",
    color_continuous_scale=px.colors.cyclical.IceFire,
    projection="orthographic"
)

# update the figure layout with open-street-map and margins
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Define your data
app.layout = dmc.Card(
    children=[
        dmc.Group(
            children=[
                dmc.TextInput(
                    id="search-input",
                    placeholder="Search for location...",
                    icon=DashIconify(icon="mdi:map-marker"),
                    style={"width": "95%"},
                ),
                dmc.Button(
                    DashIconify(icon="mdi:magnify"),
                    variant="gradient",
                    style={"width": "4%", "fontSize": "1.8rem"},
                    n_clicks=0,
                    id="search-button",
                )
            ],
            spacing="xs",
        ),
        dmc.Group(
            children=[
                dmc.Text(
                    id="weather",
                    weight=700,
                    size="lg",
                ),
            ],
            spacing="xs",
        ),
        dcc.Graph(id='map', figure={}, style={"height": "80%"}),
    ],
    shadow="sm",
    radius="md",
    style={
        "width": "80%",
        "height": "80%",
        "margin": "0 auto",
    },
)


@app.callback(
    Output("weather", "children"),
    Output("map", "figure"),
    [Input("search-button", "n_clicks")],
    [State("search-input", "value")],
)
def get_weather_and_map(n_clicks, location):
    # Check if location is provided
    if not location:
        return "Please enter a location", {}

    # Get weather data for location
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid=937baab680701220667de612cec76331'
    response = requests.get(url)
    data = response.json()
    weather = data.get('weather', [{}])[0].get('description', '')

    # Get latitude and longitude of entered location
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(location)
    if not location:
        return f"We could not find {location}", {}

    lat, lon = location.latitude, location.longitude

    # Create map figure

    fig = px.scatter_mapbox(
        lat=[lat],
        lon=[lon],
        zoom=10,
    )

    fig.update_layout(
        mapbox_style='open-street-map',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hovermode='closest'
    )

    fig.update_traces(
        marker=dict(
            size=20,
            opacity=0.9,
            color='red'
        ),
        selector=dict(mode='markers'),

    )

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        )
    )

    return weather, fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
