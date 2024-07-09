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
from dash import dcc
from PIL import Image
import re
from wasp_tool_dash import utilities
from urllib.parse import urlparse
from config import KEY, SECRET_KEY

STYLE_TEXT = {
    "color": "black",
    "marginLeft": "50px",
    "marginRight": "50px",
    "marginTop": "50px",
    "marginBottom": "50px",
    "text-align": "left",
    "text-align-last": "left",
    "font-size": "auto",
}

STYLE_INFO = {
    "color": "white",
    "marginLeft": "50px",
    "marginRight": "50px",
    "marginTop": "50px",
    "marginBottom": "50px",
    "text-align": "left",
    "text-align-last": "left",
    "font-size": "auto",
    "box-shadow": "2px 2px 8px rgba(0, 0, 0, 0.2)",
    "background-color": "#00263A",
    "bevel": "true",
    "width": "auto",
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
    "margin": "50px, 50px, 50px, 50px",
    "maxHeight": "500px",
    "maxWidth": "100%",
    "overflow": "scroll",
    "color": "black",
    "font-size": "25px",
}


def populate_inputs(aws_client: botocore.client, aws_bucket: str,  key: str) -> list:
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

   
    source_path = f"{key}satbeams.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]

        )
        df = pd.read_csv(obj, header=0)
    accepted_inputs = df.iloc[:, 0].tolist()
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
        
        if sat in df.iloc[:, 0].values:
            df_subset = df[df.iloc[:, 0] == sat]
            position = str(df_subset.iloc[0,2])
            norad = str(df_subset.iloc[0,3])
            beacon = str(df_subset.iloc[0,4])
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
                style=STYLE_INFO,
            )
        return html.P("Information not available.", style=STYLE_INFO)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_INFO
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
            return html.P([tle_1, html.Br(), tle_2], style=STYLE_INFO)
        return html.P("Information not available.", style=STYLE_INFO)
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
        obj = aws_client.get_object(Bucket=aws_bucket, Key=csv_path)["Body"]
        df = pd.read_csv(obj, header=0)

        if sat in df.iloc[:, 0].values:
            df_subset = df[df.iloc[:, 0] == sat]
            image_keys = df_subset.iloc[0, 5].split(",")
            
            titles = eval(df_subset.iloc[0, 6])
            urls = extract_jpg_urls(image_keys)

            # Create clickable buttons and preview windows for each URL
            children = []
            for title, url in zip(titles, urls):
                children.append(
                        html.A(
                            html.Button(title),  # Display title as button text
                            href=url,
                            target="_blank",  # Open in a new tab
                            style={"width": "100%", "margin": "10px", "text-align": "center","font-size": "20px"},
                        )
                )

            return html.Div(children,  style={"margin-right": "10px", "display": "grid", "grid-template-columns": "repeat(3,1fr)", "margin": "10px,10px,10px,10px", "width": "100%"})
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_TEXT
    )

def extract_jpg_urls(string_list):
    # Define the regex pattern for URLs ending with ".jpg"
    pattern = r"https?://.*\.(?:jpg|jpeg)"

    # Initialize an empty list to store the extracted URLs
    jpg_urls = []

    for s in string_list:
        # Find all matches in the string
        matches = re.findall(pattern, s)
        jpg_urls.extend(matches)

    return jpg_urls


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
                html.Div(utilities.create_data_table(df), style=STYLE_DATA_TABLE),
            ]
            return html.Div(children=children)
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.",
        style=STYLE_TEXT,
    )
