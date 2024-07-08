"""
This modules deines functions for populating Dash callbacks.

FUNCTIONS
    def populate_inputs(aws_client: botocore.client, aws_bucket: str, key: str) -> list:
        Populate the search dropdown with all valid satellites.
    def load_sources(aws_client: botocore.client, aws_bucket: str, key: str) -> list:
        Loads csv files from the AWS bucket to create a master list of all primary satellite
        names.
    def populate_general_info(
        aws_client: botocore.client, aws_bucket: str, sat: str, key: str
    ) -> html.P:
        Populates the 'General Info' tab by pulling information from the satbeams.csv file.
    def populate_tles(aws_client: botocore.client, aws_bucket: str, sat: str, key: str) -> html.P:
        Populates the 'TLE' tab by pulling information from the celestrak.csv file.
    def populate_footprints(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
        Populates the 'Footprints' tab with footprints images and image titles.
    def populate_freq_plans(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
        Populates the 'Frequency Plans' tab with frequency plan images.
    def populate_channels(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
        Populates the 'Channels' tab including the column filter and filter by values as well as
        the Dash datatable.
"""
from io import BytesIO, StringIO

import botocore
import pandas as pd
from dash import html
from PIL import Image

from wasp_tool_dash import utilities
from config import KEY, SECRET_KEY

STYLE_TEXT = {
    "color": "black",
    "margin": "75px",
    "text-align": "left",
    "text-align-last": "left",
    "font-size": "25px",
}

STYLE_IMAGES = {
    "margin": "50px",
    "maxHeight": "550px",
    "maxWidth": "1100px",
    "overflow": "scroll",
    "color": "black",
    "font-size": "25px",
}

STYLE_DATA_TABLE = {
    "margin": "100px",
    "maxHeight": "auto",
    "maxWidth": "auto",
    "overflow": "scroll",
    "color": "black",
    "font-size": "25px",
}


def populate_inputs() -> list:
    """
    Populate the search dropdown with all valid satellites.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    key: str
        String containing prefix check condition

    Returns
    -------
    input_options

        List of possible search options
    """
    accepted_inputs = ["H2SAT", "ABS-2", "GALAXY 16", "Bsat 3B"]
    accepted_inputs.sort() 
    return accepted_inputs


def populate_general_info(aws_client: botocore.client, aws_bucket: str, sat: str, key: str) -> html.P:
    """
    Populates the General Info tab by pulling information from the satbeams.csv file.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    sat: str
        String containing satellite chosen in the search dropdown
    key: str
        String containing prefix check condition

    Returns
    -------
    html.P
        if data exists and is available, returns data
        is data is not available, returns "information not available" message
        if data does not exist, returns "populate data sources" message
    """
    source_path = f"{key}satbeams.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]
            
        )
        df = pd.read_csv(obj, header=0)
        
        if sat in df["Primary Satellite Name"].values or sat in df["Secondary Satellite Name(s)"].values:
            df_subset = df[df["Primary Satellite Name"] == sat]
            position = str(df_subset["Position"].iloc[0])
            norad = str(df_subset["NORAD ID"].iloc[0])
            beacon = str(df_subset["Beacons"].iloc[0])
            return html.P(
                [
                    "Satellite: " + sat,
                    html.Br(),
                    "Position: " + position,
                    html.Br(),
                    "NORAD: " + norad,
                    html.Br(),
                    "Beacon(s): " + beacon,
                ],
                style=STYLE_TEXT,
            )
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_TEXT
    )


def populate_tles(
    aws_client: botocore.client, aws_bucket: str, sat: str, key: str
) -> html.P:
    """
    Populates the 'TLE' tab by pulling information from the celestrak.csv file.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    sat: str
        String containing satellite chosen in the search dropdown
    key: str
        String containing prefix check condition

    Returns
    -------
    html.P
        if data exists and is available, returns data
        is data is not available, returns "information not available" message
        if data does not exist, returns "populate data sources" message
    """
    source_path = f"{key}celestrak.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]

        )
        df = pd.read_csv(obj, header=0)
        if sat in df["Primary Satellite"].values :
            df_subset = df[df["Primary Satellite"] == sat]
            tle_1 = df_subset["TLE-1"].tolist()[0]
            tle_2 = df_subset["TLE-2"].tolist()[0]
            return html.P([tle_1, html.Br(), tle_2], style=STYLE_TEXT)
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_TEXT
    )


def populate_footprints(
    aws_client: botocore.client, aws_bucket: str, sat: str, key: str
):
    """
    Populates the 'Footprints' tab with footprints images and image titles.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    sat: str
        String containing satellite chosen in the search dropdown
    key: str
        String containing prefix check condition

    Returns
    -------
    html.Div
        if data exists, returns footprint images and image titles
    html.P
        is data is not available, returns "information not available" message
        if data does not exist, returns "populate data sources" message
    """
    csv_path = f"{key}satbeams.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=csv_path)["Body"]

        )
        df = pd.read_csv(obj, header=0)
        if sat in df["Primary Satellite"].values:
            source_path = f"{key}footprints/{sat}/"
            image_keys = utilities.get_file_keys(
                aws_client, aws_bucket, source_path, ".jpg"
            )
            children = []
            for image in image_keys:
                title = image.rsplit("/", maxsplit=1)[1]
                title = title.replace(".jpg", "")
                file_stream = BytesIO()
                aws_client.download_fileobj(aws_bucket, image, file_stream)
                img = Image.open(file_stream)
                children.append(title)
                children.append(html.Img(src=img))
            return html.Div(children, style=STYLE_IMAGES)
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_TEXT
    )


def populate_freq_plans(
    aws_client: botocore.client, aws_bucket: str, sat: str, key: str
):
    """
    Populates the 'Frequency Plans' tab with frequency plan images.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    sat: str
        String containing satellite chosen in the search dropdown
    key: str
        String containing prefix check condition

    Returns
    -------
    html.Div
        if data exists, returns frequency plan images
    html.P
        is data is not available, returns "information not available" message
        if data does not exist, returns "populate data sources" message
    """
    csv_path = f"{key}altervista.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=csv_path)["Body"]

        )
    df = pd.read_csv(obj, header=0)
    if sat in df["Primary Satellite"].values:
        df_subset = df[df["Primary Satellite"] == sat]
        image_url = df_subset["Frequency Plan URL"].values[0]

        return html.Div([
            html.Iframe(src=image_url, style={
                        'width': '100%', 'height': '700px'}),
        ])
    else:
        return html.P("Information not available.", style=STYLE_TEXT)



def populate_channels(aws_client: botocore.client, aws_bucket: str, sat: str, key: str):
    """
    Populates the 'Channels' tab including the column filter and filter by values as well as
    the Dash datatable.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    sat: str
        String containing satellite chosen in the search dropdown
    key: str
        String containing prefix check condition

    Returns
    -------
    html.Div
        if data exists, returns column filters with filter by options and populated datatable
    html.P
        is data is not available, returns "information not available" message
        if data does not exist, returns "populate data sources" message
    """
    csv_path = f"{key}lyngsat.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=csv_path)["Body"]
    
        )
        df = pd.read_csv(obj, header=0)
        if sat in df["Primary Satellite Name"].values:
            source_path = f"{key}channels/{sat}/{sat}.csv"
            obj = (
                aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]
            )
            df = pd.read_csv(obj, header=0)
            children = [
                html.Div(
                    children=[
                        utilities.create_column_filter(),
                        utilities.create_value_filter(),
                    ],
                    style={"margin": "40px"},
                ),
                html.Div(utilities.create_data_table(df), style=STYLE_DATA_TABLE),
            ]
            return html.Div(children=children)
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.",
        style=STYLE_TEXT,
    )
