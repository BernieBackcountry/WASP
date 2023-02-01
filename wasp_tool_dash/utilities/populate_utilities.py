from dash import html
import pandas as pd
from dash import dash_table
from pathlib import Path

import wasp_tool_dash.utilities as utilities


def populate_inputs(path: Path) -> dict:
    path_data = path.joinpath('data')
    sources = ['celestrak.csv', 'satbeams.csv', 'lyngsat.csv', 'altervista.csv']
    accepted_inputs = []
    for source in sources:
        source_path = path_data.joinpath(source)
        if source_path.exists():
            accepted_inputs.extend(load_sources(source_path, source))
    
    accepted_inputs = list(set(accepted_inputs))
    accepted_inputs.sort()
    input_options = [{'label': accepted_input, 'value': accepted_input} for accepted_input in accepted_inputs]
    return input_options
    
    
def load_sources(path: Path, source: str) -> list:
    df_source = pd.read_csv(f'{path}', header=0)
    source_inputs = df_source['priSatName'].tolist()
    return source_inputs


def populate_general_info(sat: str, satbeam_satellites: list, df_satbeam: pd.DataFrame):
    style = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat in satbeam_satellites:
        df = df_satbeam[df_satbeam['priSatName'] == sat.upper()]
        sat_id = sat.upper()
        position = str(df['Position'].iloc[0])
        norad = str(df['NORAD ID'].iloc[0])
        beacon = str(df['Beacons'].iloc[0])
        return html.P(["Satellite: " + sat_id, html.Br(), "Position: " + position, html.Br(), "NORAD: " + norad, html.Br(), "Beacon(s): " + beacon], 
                        style=style)
    else:
        return html.P("Information not available.", style=style)


def populate_telemetry(sat: str, celestrak_satellites: list, df_celestrak: pd.DataFrame):
    style = {'color': "black", 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat in celestrak_satellites:
        df = df_celestrak[df_celestrak['priSatName'] == sat.upper()]
        temp = str(df['TLE'].iloc[0]).split("\n", 1)
        tle_1 = temp[0]
        tle_2 = temp[1]
        return html.P([tle_1, html.Br(), tle_2], style=style)
    else:
        return html.P("Information not available.", style=style)


def populate_footprints(sat: str, satbeam_satellites: list):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat in satbeam_satellites:
        path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')
        path = path.joinpath('data', 'footprints')
        images = path.joinpath(sat).glob('*.jpg')
        children=[]
        for image in images:
            children.append(image.stem)
            children.append(utilities.encode_image(image))
        return html.Div(children, style=style1)
    else:
        return html.P("Information not available.", style=style2)


def populate_freq_plans(sat: str, altervista_satellites: list):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat in altervista_satellites:
        path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')
        path = path.joinpath('data', 'freq_plans', sat)
        freq_plans = path.glob('*.jpg')
        children = []
        for plan in freq_plans:
            children.append(utilities.encode_image_pdf(plan))
        return html.Div(children, style=style1)
    else:
        return html.P("Information not available.", style=style2)



def populate_channels(sat: str, lyngsat_satellites: list):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if sat in lyngsat_satellites:
        path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')
        path = path.joinpath('data', 'channels')
        csvs = path.joinpath(sat).glob('*.csv')
        children = []
        dfs = []
        for csv in csvs:
            temp = pd.read_csv(csv)
            temp.drop("Satellite", axis=1, inplace=True)
            dfs.append(temp)
        df = pd.concat(dfs)
        children = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], style_cell ={'fontSize':14})
        return html.Div(children, style=style1)
    else:
        return html.P("Information not available.", style=style2)

