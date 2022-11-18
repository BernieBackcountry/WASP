import dash
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd
from pathlib import Path


import scraper_dash.utilities as utilities 


path = utilities.get_project_path().resolve().parent.joinpath('scraper')
path_celestrak = path.joinpath('data','celestrak.csv')
path_satbeam = path.joinpath('data','satbeam.csv')

df_celestrak = pd.read_csv(path_celestrak, header=0)
df_satbeam = pd.read_csv(path_satbeam, header=0)

celestrak_satellites = df_celestrak['Satellite'].tolist()
satbeam_satellites = df_satbeam['Satellite'].tolist()
acceptable_satellites = list(set(celestrak_satellites + satbeam_satellites))


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = utilities.create_layout()


# Call back for search bar
@app.callback(
    Output(component_id='search-message', component_property='children'),
    [Input(component_id='sat-id', component_property='value')])
def get_general_info(sat: str):
    if sat is None:
        raise PreventUpdate
    else:
        if sat.upper() in acceptable_satellites:
            return html.P("Click a tab to view information for " + sat.upper())
        else:
            return html.P(sat + " is not a valid satellite input.")


# Callback for tab navigation - fill textbox dependent on tab id
@app.callback(Output('tabs-content', 'children'),
              [Input(component_id='sat-id', component_property='value'), Input('tabs', 'value')])
def render_content(sat: str, tab):
    if sat is None:
        raise PreventUpdate
    else:
        if sat.upper() in acceptable_satellites:
            if tab == 'tab-general':
                return populate_general_info(sat) 
            elif tab == 'tab-telemetry':
                return populate_telemetry(sat)
            elif tab == 'tab-footprints':
                return populate_footprints(sat)
        return ""


def populate_general_info(sat: str):
    if sat.upper() in satbeam_satellites:
        df = df_satbeam[df_satbeam['Satellite'] == sat.upper()]
        sat_id = sat.upper()
        position = str(df['Position'].iloc[0])
        norad = str(df['NORAD'].iloc[0])
        beacon = str(df['Beacon'].iloc[0])
        return html.P(["Satellite: " + sat_id, html.Br(), "Position: " + position, html.Br(), "NORAD: " + norad, html.Br(), "Beacon(s): " + beacon], 
                        style={'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'})
    else:
        return html.P("Information not available.", 
                        style={'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'})


def populate_telemetry(sat: str):
    if sat.upper() in celestrak_satellites:
        df = df_celestrak[df_celestrak['Satellite'] == sat.upper()]
        temp = str(df['Telemetry'].iloc[0]).split("\n", 1)
        tle_1 = temp[0]
        tle_2 = temp[1]
        return html.P([tle_1, html.Br(), tle_2], style={'color': "black", 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'})
    else:
        return html.P("Information not available.", 
                        style={'color': "black", 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'})


def populate_footprints(sat: str):
    if sat.upper() in satbeam_satellites:
        path = utilities.get_project_path().resolve().parent.joinpath('scraper')
        path = path.joinpath('data', 'images')
        images = path.joinpath(sat.upper()).glob('*.jpg')
        children = []
        for image in images:
            children.append(image.stem)
            children.append(utilities.encode_image(image))
        return html.Div(children, style={'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'})
    else:
        return html.P("Information not available.", 
                        style={'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'})


if  __name__ == '__main__':
    app.run_server(debug=True)