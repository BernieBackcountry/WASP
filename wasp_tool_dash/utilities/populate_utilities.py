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
import boto3
import numpy as np
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
import math
import dash
from config import BUCKET_NAME, KEY, SECRET_KEY, API_KEY, access_token
from skyfield.api import Topos, load,EarthSatellite


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

LATITUDE = None
LONGITUDE = None


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


def populate_general_info(aws_client: botocore.client, aws_bucket: str, sat: str, norad: str, key: str) -> html.P:
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
    try: 
        source_path = f"{key}satbeams.csv"
        does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
        if does_exist:
            obj = (
                aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]

            )
            df = pd.read_csv(obj, header=0)

            if norad in df.iloc[:, 3].values:
                df_subset = df[df.iloc[:, 3] == norad]
                position = str(df_subset.iloc[0, 2])
                norad = str(df_subset.iloc[0, 3])
                beacon = str(df_subset.iloc[0, 4])
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
    except Exception as e:  
        return html.P(
            "Populate data sources to obtain requested information.", style=STYLE_INFO
        )


def populate_tles(
    aws_client: botocore.client, aws_bucket: str, norad: str, key: str
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
    try:
        source_path = f"{key}celestrak.csv"
        does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
        if does_exist:
            obj = (
                aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]

            )
            df = pd.read_csv(obj, header=0)
            if norad in df["Norad"].values:
                df_subset = df[df["Norad"] == norad]
                tle_1 = df_subset["TLE-1"].tolist()[0]
                tle_2 = df_subset["TLE-2"].tolist()[0]
                return html.P([tle_1, html.Br(), tle_2], style=STYLE_INFO)
            return html.P("Information not available.", style=STYLE_INFO)
    except Exception as e:
        return html.P(
            "Populate data sources to obtain requested information.",  style=STYLE_INFO
        )


def populate_footprints(
    aws_client: botocore.client, aws_bucket: str, sat: str, norad: str, key: str
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
    try:
        csv_path = f"{key}satbeams.csv"
        does_exist = utilities.prefix_exists(aws_client, aws_bucket, csv_path)
        if does_exist:
            obj = aws_client.get_object(Bucket=aws_bucket, Key=csv_path)["Body"]
            df = pd.read_csv(obj, header=0)

            if norad in df.iloc[:, 3].values:
                df_subset = df[df.iloc[:, 3] == norad]
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
                            style={
                                "width": "100%",
                                "display": "block",
                                "margin": "10px",
                                "padding": "10px",
                                "text-align": "center",
                                "font-size": "auto",
                                "white-space": "nowrap",
                                "text-overflow": "ellipsis",
                                "box-shadow": "2px 2px 8px rgba(0, 0, 0, 0.2)",
                                "background-color": "#FFFFFF",
                                "font-color": "white",
                            }
                        )
                    )

                return html.Div(children,  style={"margin": "10px",
                                                "padding": "10px",
                                                "display": "grid",
                                                "grid-template-columns": "repeat(auto-fit, minmax(min(260px, 50%), max(600px, 50%)))",
                                                "align-items": "right", })
            return html.P("Information not available.", style=STYLE_INFO)
    except Exception as e:
        return html.P(
            "Populate data sources to obtain requested information.", style=STYLE_INFO
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
    try:
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
            menlo_url = "https://safe.menlosecurity.com/" +image_url[len("http://"):]

            return html.Div([
                html.Iframe(src=image_url, style={
                            'width': '100%', 'height': '500px'}),html.Br(),
                html.A("Click here to view the Frequency Plans on NIPR", href=menlo_url, target="_blank", style={
                    'font-size': '20px', 'color': '#00263A', 'text-decoration': 'underline'}),html.Br(),
                html.A("Click here to view the Frequency Plans if not diplayed", href=image_url, target="_blank", style={
                    'font-size': '20px', 'color': '#00263A', 'text-decoration': 'underline'}),
            ])
        return html.P("Information not available.", style=STYLE_INFO)
    except Exception as e:
        return html.P("Populate data sources to obtain requested information.", style=STYLE_INFO)


def populate_channels(aws_client: botocore.client, aws_bucket: str, sat: str, norad: str, key: str):
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
    norad: str
        String containing Norad ID
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
        try:
            obj_lyngsat = aws_client.get_object(
                Bucket=aws_bucket, Key=csv_path)["Body"]
        except:
            return html.P("Information not available.", style=STYLE_INFO)
        

        df = pd.read_csv(obj_lyngsat, header=0)
        # Apply the function to the entire column
        # df["Primary Satellite Name"] = df["Primary Satellite Name"].apply(lambda x: sat if x == 'Satellite' else x)

        if sat in df["Primary Satellite Name"].values:
            source_path = f"{key}channels/{sat}/{sat}.csv"
            obj = aws_client.get_object(
                Bucket=aws_bucket, Key=source_path)["Body"]
            df_lyngsat = pd.read_csv(obj, header=0)
            children = [html.Div(utilities.create_data_table(
                df_lyngsat), style=STYLE_DATA_TABLE)]
            return html.Div(children=children)
        return html.P("Information not available.", style=STYLE_INFO)
    return html.P("Populate data sources to obtain requested information.", style=STYLE_INFO)


def dish_pointer(aws_client: botocore.client, aws_bucket: str, norad: str, latitude: float, longitude: float) -> tuple:
    """
    Calculates the dish pointing angle for a satellite based on the user's location.

    Parameters
    ----------
    aws_client: botocore.client
        AWS S3 client
    aws_bucket: str
        AWS S3 bucket name
    norad: str
        NORAD ID of the satellite
    key: str
        Key for the satellite data file
    latitude: float
        User's latitude
    longitude: float
        User's longitude

    Returns
    -------
    tuple
        Azimuth and Elevation angles in degrees
    """

    # Load satellite data from S3
    source_path = f"satbeams.csv"
    if utilities.prefix_exists(aws_client, aws_bucket, source_path):
        obj = aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]
        df = pd.read_csv(obj, header=0)

        # Get Celestrak data
        source_path = f"celestrak.csv"
        if utilities.prefix_exists(aws_client, aws_bucket, source_path):
            obj = aws_client.get_object(
                Bucket=aws_bucket, Key=source_path)["Body"]
            df = pd.read_csv(obj, header=0)

            # Calculate azimuth and elevation
            if norad in df["Norad"].values:
                df_subset = df[df["Norad"] == norad]
                try:
                    # Retrieve and format TLE data
                    tle_1 = df_subset["TLE-1"].tolist()[0].replace("*", " ")
                    tle_2 = df_subset["TLE-2"].tolist()[0].replace("*", " ")
                    satellite_name = df_subset["Primary Satellite"].tolist()[0]

                    # Get the time from Skyfield (you can use other time sources as well)
                    ts = load.timescale()
                    t = ts.now()

                    # Use the satellite name as the key
                    satellite = EarthSatellite(tle_1, tle_2, satellite_name, ts)

                    # Create a location for the observer
                    observer = Topos(latitude_degrees=float(latitude),
                                    longitude_degrees=float(longitude))

                    # Calculate the position of the satellite relative to the observer
                    difference = satellite - observer

                    # Get the azimuth and elevation angles
                    topocentric = difference.at(t)
                    alt, az, distance = topocentric.altaz()

                    return az.degrees, alt.degrees

                except Exception as e:
                    print(f"Error calculating satellite angles: {e}")
                    return 0.0, 0.0  # Return default values or handle error as needed


def update_lat_long_and_calculate(n_clicks, latitude, longitude, aws_client: botocore.client, aws_bucket: str, norad: str, key: str):
    """
    Callback to update latitude and longitude inputs and recalculate azimuth and elevation.

    Parameters
    ----------
    n_clicks: int
        Number of button clicks.
    latitude: str
        Latitude input value.
    longitude: str
        Longitude input value.

    Returns
    -------
    list of updated values for latitude, longitude, azimuth, elevation, and map src.
    """

    if n_clicks:
        global LATITUDE, LONGITUDE
        LATITUDE = float(latitude)
        LONGITUDE = float(longitude)

        # Recalculate azimuth and elevation based on the new latitude and longitude
        azimuth, elevation = dish_pointer(
            aws_client=aws_client,  # Replace with actual AWS client
            aws_bucket=aws_bucket,  # Replace with your AWS bucket name
            norad=norad,  # Replace with the NORAD ID
            latitude=LATITUDE,
            longitude=LONGITUDE,
        )

        # Update the map iframe src
        map_src = f"https://www.google.com/maps/embed/v1/place?key={
            API_KEY}&q={LATITUDE},{LONGITUDE}"

        # Return updated values
        return LATITUDE, LONGITUDE, f"{azimuth:.2f}°", f"{elevation:.2f}°", map_src

    # If the button hasn't been clicked, return the current state
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
