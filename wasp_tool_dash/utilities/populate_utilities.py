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
            accepted_inputs.extend(load_sources(source_path))
    
    accepted_inputs = list(set(accepted_inputs))
    accepted_inputs.sort()
    input_options = [{'label': accepted_input, 'value': accepted_input} for accepted_input in accepted_inputs]
    return input_options
    
    
def load_sources(path: Path) -> list:
    df_source = pd.read_csv(f'{path}', header=0)
    source_inputs = df_source['priSatName'].tolist()
    return source_inputs


def populate_general_info(sat: str, path: Path):
    style = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if path.joinpath('data', 'satbeams.csv').exists():
        source_path = path.joinpath('data', 'satbeams.csv')
        df = pd.read_csv(f'{source_path}', header=0)
        if sat in df['priSatName'].values:
            df_subset = df[df['priSatName'] == sat]
            position = str(df_subset['Position'].iloc[0])
            norad = str(df_subset['NORAD ID'].iloc[0])
            beacon = str(df_subset['Beacons'].iloc[0])
            return html.P(["Satellite: " + sat, html.Br(), "Position: " + position, html.Br(), "NORAD: " + norad, html.Br(), "Beacon(s): " + beacon], 
                            style=style)
        else:
            return html.P("Information not available.", style=style)

    else:
        return html.P("Populate data sources to obtain requested information.", style=style)


def populate_telemetry(sat: str, path: Path):
    style = {'color': "black", 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if path.joinpath('data', 'celestrak.csv').exists():
        source_path = path.joinpath('data', 'celestrak.csv')
        df = pd.read_csv(f'{source_path}', header=0)
        if sat in df['priSatName'].values:
            df_subset = df[df['priSatName'] == sat]
            temp = str(df_subset['TLE'].iloc[0]).split("\n", 1)
            tle_1 = temp[0]
            tle_2 = temp[1]
            return html.P([tle_1, html.Br(), tle_2], style=style)
        else:
            return html.P("Information not available.", style=style)
    else:
        return html.P("Populate data sources to obtain requested information.", style=style)


def populate_footprints(sat: str, path: Path):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if path.joinpath('data', 'footprints').exists():
        if path.joinpath('data', 'footprints', sat).exists():
            source_path = path.joinpath('data', 'footprints', sat)
            images = source_path.glob('*.jpg')
            children=[]
            for image in images:
                children.append(image.stem)
                children.append(utilities.encode_image(image))
            return html.Div(children, style=style1)

        else:
            return html.P("Information not available.", style=style2)
    else:
        return html.P("Populate data sources to obtain requested information.", style=style2)

def populate_freq_plans(sat: str, path: Path):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if path.joinpath('data', 'freq_plans').exists():
        if path.joinpath('data', 'freq_plans', sat).exists():
            source_path = path.joinpath('data', 'freq_plans', sat)
            images = source_path.glob('*.jpg')
            children=[]
            for image in images:
                children.append(utilities.encode_image_pdf(image))
            return html.Div(children, style=style1)
        else:
            return html.P("Information not available.", style=style2)
    else:
        return html.P("Populate data sources to obtain requested information.", style=style2)



def populate_channels(sat: str, path: Path):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': "black", 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    if path.joinpath('data', 'channels').exists():
        if path.joinpath('data', 'channels', sat).exists():
            dfs = source_path.glob('*.csv')
            source_path = path.joinpath('data', 'channels', sat)
            tables = []
            for df in dfs:
                temp = pd.read_csv(df)
                temp.drop("Satellite", axis=1, inplace=True)
                tables.append(temp)
            master_table = pd.concat(tables)
            children = dash_table.DataTable(master_table.to_dict('records'), [{"name": i, "id": i} for i in master_table.columns], style_cell ={'fontSize':14})
            return html.Div(children, style=style1)
        else:
            return html.P("Information not available.", style=style2)
    else:
        return html.P("Populate data sources to obtain requested information.", style=style2)

