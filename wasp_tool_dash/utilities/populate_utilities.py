from dash import html
import pandas as pd
from pdf2image import convert_from_path
from dash import dash_table

import wasp_tool_dash.utilities as utilities


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
        children = []
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
        path = path.joinpath('data', 'freq_plans')
        pdfs = path.joinpath(sat).glob('*.pdf')
        for pdf in pdfs:
            pages = convert_from_path(pdf)
            for i, page in enumerate(pages):
                file_path = path.joinpath(sat)
                file_name = sat + "_" + str(i) + ".jpg"
                page.save(file_path / file_name, 'JPEG')
        freq_plans = path.joinpath(sat).glob('*.jpg')
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
            dfs.append(pd.read_csv(csv))
        df = pd.concat(dfs)
        children = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], style_data ={'width': '5%'})
        return html.Div(children, style=style1)
    else:
        return html.P("Information not available.", style=style2)

