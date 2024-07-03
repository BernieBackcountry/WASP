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
    "margin": "50px",
    "maxHeight": "500px",
    "maxWidth": "1200px",
    "overflow": "scroll",
    "color": "black",
    "font-size": "25px",
}


def populate_inputs(aws_client: botocore.client, aws_bucket: str, key: str) -> list:
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
    sources = ["celestrak.csv", "satbeams.csv", "lyngsat.csv", "altervista.csv"]
    accepted_inputs = []
    for source in sources:
        source_path = key + source
        does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)

        if does_exist:
            accepted_inputs.extend(load_sources(aws_client, aws_bucket, source_path))
            print("it exists")

    accepted_inputs = list(set(accepted_inputs))
    accepted_inputs.sort()
    input_options = [
        {"label": accepted_input, "value": accepted_input}
        for accepted_input in accepted_inputs
    ]
    return input_options


def load_sources(aws_client: botocore.client, aws_bucket: str, key: str) -> list:
    """
    Loads csv files from the AWS bucket to create a master list of all primary satellite
    names.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    key: str
        String containing prefix determing objects to grab

    Returns
    -------
    source_inputs: lsit
        List of all primary satellite names
    """

    obj = aws_client.get_object(Bucket=aws_bucket, Key= key)["Body"].read().decode("utf-8")
    df_source = pd.read_csv(StringIO(obj), header=0)
    source_inputs = df_source["Primary Satellite Name"].tolist()

    return source_inputs


def populate_general_info(
    aws_client: botocore.client, aws_bucket: str, sat: str, key: str
) -> html.P:
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
            .read()
            .decode("utf-8")
        )
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df["Primary Satellite Name"].values:
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
            .read()
            .decode("utf-8")
        )
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df["Primary Satellite Name"].values:
            df_subset = df[df["Primary Satellite Name"] == sat]
            temp = str(df_subset["TLES"].iloc[0]).split("\n", maxsplit=1)
            tle_1 = temp[0]
            tle_2 = temp[1]
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
            .read()
            .decode("utf-8")
        )
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df["Primary Satellite Name"].values:
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
            .read()
            .decode("utf-8")
        )
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df["Primary Satellite Name"].values:
            source_path = key + "freq_plans/" + sat + "/"
            image_keys = utilities.get_file_keys(
                aws_client, aws_bucket, source_path, ".jpg"
            )
            children = []
            for image in image_keys:
                file_stream = BytesIO()
                aws_client.download_fileobj(aws_bucket, image, file_stream)
                img = Image.open(file_stream)
                children.append(html.Img(src=img, style={"width": "95%"}))
            return html.Div(children, style=STYLE_IMAGES)
        return html.P("Information not available.", style=STYLE_TEXT)
    return html.P(
        "Populate data sources to obtain requested information.", style=STYLE_TEXT
    )


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
            .read()
            .decode("utf-8")
        )
        df = pd.read_csv(StringIO(obj), header=0)
        if sat in df["Primary Satellite Name"].values:
            source_path = f"{key}channels/{sat}/{sat}.csv"
            obj = (
                aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]
                .read()
                .decode("utf-8")
            )
            df = pd.read_csv(StringIO(obj), header=0)
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
