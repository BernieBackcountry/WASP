from dash import html
import pandas as pd

import scraper_dash.utilities as utilities


def populate_general_info(sat: str, satbeam_satellites: list, df_satbeam: pd.DataFrame):
    style = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat.upper() in satbeam_satellites:
        df = df_satbeam[df_satbeam['Satellite'] == sat.upper()]
        sat_id = sat.upper()
        position = str(df['Position'].iloc[0])
        norad = str(df['NORAD'].iloc[0])
        beacon = str(df['Beacon'].iloc[0])
        return html.P(["Satellite: " + sat_id, html.Br(), "Position: " + position, html.Br(), "NORAD: " + norad, html.Br(), "Beacon(s): " + beacon], 
                        style=style)
    else:
        return html.P("Information not available.", style=style)


def populate_telemetry(sat: str, celestrak_satellites: list, df_celestrak: pd.DataFrame):
    style = {'color': "black", 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat.upper() in celestrak_satellites:
        df = df_celestrak[df_celestrak['Satellite'] == sat.upper()]
        temp = str(df['Telemetry'].iloc[0]).split("\n", 1)
        tle_1 = temp[0]
        tle_2 = temp[1]
        return html.P([tle_1, html.Br(), tle_2], style=style)
    else:
        return html.P("Information not available.", style=style)


def populate_footprints(sat: str, satbeam_satellites: list):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat.upper() in satbeam_satellites:
        path = utilities.get_project_path().resolve().parent.joinpath('scraper')
        path = path.joinpath('data', 'images')
        images = path.joinpath(sat.upper()).glob('*.jpg')
        children = []
        for image in images:
            children.append(image.stem)
            children.append(utilities.encode_image(image))
        return html.Div(children, style=style1)
    else:
        return html.P("Information not available.", style=style2)