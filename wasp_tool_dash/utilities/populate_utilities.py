from io import BytesIO, StringIO

import botocore
import pandas as pd
from dash import html
from PIL import Image

import wasp_tool_dash.utilities as utilities


def populate_inputs(aws_client: botocore.client, aws_bucket: str, key: str) -> dict:
    sources = ['celestrak.csv', 'satbeams.csv', 'lyngsat.csv', 'altervista.csv']
    accepted_inputs = []
    for source in sources:
        source_path = key + source
        does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
        if does_exist:
            accepted_inputs.extend(load_sources(aws_client, aws_bucket, source_path))
 
    accepted_inputs = list(set(accepted_inputs))
    accepted_inputs.sort()
    input_options = [{'label': accepted_input, 'value': accepted_input} for accepted_input in accepted_inputs]
    return input_options
    
    
def load_sources(aws_client: botocore.client, aws_bucket: str, key: str) -> list:
    obj = aws_client.get_object(Bucket=aws_bucket, Key=key)['Body'].read().decode('utf-8')
    df_source = pd.read_csv(StringIO(obj), header=0)
    source_inputs = df_source['priSatName'].tolist()
    return source_inputs


def populate_general_info(aws_client: botocore.client, aws_bucket: str, sat: str, key: str) -> html.P:
    style = {'color': 'black', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    source_path = f'{key}satbeams.csv'
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = aws_client.get_object(Bucket=aws_bucket, Key=source_path)['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df['priSatName'].values:
            df_subset = df[df['priSatName'] == sat]
            position = str(df_subset['Position'].iloc[0])
            norad = str(df_subset['NORAD ID'].iloc[0])
            beacon = str(df_subset['Beacons'].iloc[0])
            return html.P(['Satellite: ' + sat, html.Br(), 'Position: ' + position, html.Br(), 'NORAD: ' + norad, html.Br(), 'Beacon(s): ' + beacon], 
                            style=style)
        else:
            return html.P('Information not available.', style=style)

    else:
        return html.P('Populate data sources to obtain requested information.', style=style)


def populate_telemetry(aws_client: botocore.client, aws_bucket: str, sat: str, key: str) -> html.P:
    style = {'color': 'black', 'left-margin': '20px', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    source_path = f'{key}celestrak.csv'
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = aws_client.get_object(Bucket=aws_bucket, Key=source_path)['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df['priSatName'].values:
            df_subset = df[df['priSatName'] == sat]
            temp = str(df_subset['TLE'].iloc[0]).split('\n', 1)
            tle_1 = temp[0]
            tle_2 = temp[1]
            return html.P([tle_1, html.Br(), tle_2], style=style)
        else:
            return html.P('Information not available.', style=style)
    else:
        return html.P('Populate data sources to obtain requested information.', style=style)


def populate_footprints(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': 'black', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    csv_path = f'{key}satbeams.csv'
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        try:
            source_path = f'{key}footprints/{sat}/'
            image_keys = utilities.get_file_keys(aws_client, aws_bucket, source_path, '.jpg')
            children = []
            for image in image_keys:
                title = image.rsplit('/', 1)[1]
                title = title.replace('.jpg', '')
                file_stream = BytesIO()
                aws_client.download_fileobj(aws_bucket, image, file_stream)
                img = Image.open(file_stream)
                children.append(title)
                children.append(html.Img(src=img))
            return html.Div(children, style=style1)     
        except:
            return html.P('Information not available.', style=style2)  
    else:
        return html.P('Populate data sources to obtain requested information.', style=style2)


def populate_freq_plans(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
    style1 = {'margin': '50px', 'maxHeight': '550px', 'maxWidth': '1100px', 'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style2 = {'color': 'black', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 'font-size': '25px'}
    csv_path = f'{key}altervista.csv'
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        try:
            source_path = f'{key}freq_plans/{sat}/'
            image_keys = utilities.get_file_keys(aws_client, aws_bucket, source_path, '.jpg')
            children = []
            for image in image_keys:
                file_stream = BytesIO()
                aws_client.download_fileobj(aws_bucket, image, file_stream)
                img = Image.open(file_stream)
                children.append(html.Img(src=img))
            return html.Div(children, style=style1)   
        except:
            return html.P('Information not available.', style=style2)     
    else:
        return html.P('Populate data sources to obtain requested information.', style=style2)


def populate_channels(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
    style_data_table = {'margin': '50px', 'maxHeight': '500px', 'maxWidth': '1200px', 
                        'overflow': 'scroll', 'color': 'black', 'font-size': '25px'}
    style_generic = {'color': 'black', 'margin': '75px', 'text-align': 'left', 'text-align-last': 'left', 
              'font-size': '25px'}
    csv_path = f'{key}lyngsat.csv'
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        try:
            source_path = f'{key}channels/{sat}/{sat}.csv'
            obj = aws_client.get_object(Bucket=aws_bucket, Key=source_path)['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(obj), header=0)
            children = [html.Div(children=[
                                 utilities.create_column_filter(),
                                 utilities.create_value_filter()], style={'margin': '40px'}),
                        html.Div(utilities.create_data_table(df), style=style_data_table)]
            return html.Div(children=children)
        except:
            return html.P('Information not available.', style=style_generic)
    else:
        return html.P('Populate data sources to obtain requested information.', style=style_generic)
