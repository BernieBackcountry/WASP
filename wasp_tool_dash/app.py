"""
This module creates the Dash application interface and pulls information from
the AWS bucket.

CALLBACKS
    def update_search_options(search: str):
        Callback to update search bar/dropdown valid options.
    def update_celestrak_tles(click: int):
        Callback to run file to pull and write CelesTrak TLEs to the AWS bucket.
    def render_content(search: str, tab: str):
        Callback to render tab content.
    def render_filter_values(column: str):
        Callback to render column filter and filter by values.
    def update_rows(column: str, value: str, sat: str):
        Callback to update datatable dependent on filter values.
"""
import os
import boto3
import dash
import pandas as pd
from dash.dependencies import Input, Output

from wasp_tool_dash import utilities
from wasp_tool_dash.utilities import populate_utilities
from wasp_tool_dash.components import LayoutCreator
from wasp_tool.prepare import get_celestrak_data
from wasp_tool_dash.utilities import dish_pointer
from config import BUCKET_NAME,KEY,SECRET_KEY,API_KEY,access_token
import datetime
import ipinfo

session = boto3.session.Session()
CURRENT_LOCATION = 1

AWS_CLIENT = session.client(
    's3',
    region_name='nyc3',
    endpoint_url="https://newsatbucket.nyc3.digitaloceanspaces.com",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET_KEY,
)

AWS_BUCKET_NAME = BUCKET_NAME

PATH_KEY = ""

path = utilities.get_project_path().joinpath("wasp_tool")

layout_creator = LayoutCreator()

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile
app.layout = layout_creator.create_layout(
    AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY
)


@app.callback(
    [Output(component_id="sat-dropdown", component_property="options"),
     Output(component_id="sat-dropdown", component_property="value")],
    [Input(component_id="tabs", component_property="value"),
     Input(component_id="sat-dropdown", component_property="options"),
     Input(component_id="sat-dropdown", component_property="value")],
    suppress_callback_exceptions=True
)
def update_options(selected_tab, dropdown_options, sat):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dropdown_options, sat

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'tabs':
        if selected_tab == 'tab-freq_plans':
            csv_path = "altervista.csv"
            try:
                obj_freq_plans = AWS_CLIENT.get_object(
                    Bucket=AWS_BUCKET_NAME, Key=csv_path)["Body"]
                df = pd.read_csv(obj_freq_plans, header=0)
                new_options = [{'label': value, 'value': value}
                               for value in df.iloc[:, 0].tolist()]
                return new_options, sat if sat else ""
            except Exception as e:
                print(f"Error fetching or reading CSV for freq plans: {e}")
                return [], ""
        elif selected_tab == 'tab-channels':
            csv_path = "lyngsat.csv"
            try:
                obj_lyngsat = AWS_CLIENT.get_object(
                    Bucket=AWS_BUCKET_NAME, Key=csv_path)["Body"]
                df = pd.read_csv(obj_lyngsat, header=0)
                new_options = [{'label': value, 'value': value}
                               for value in df.iloc[:, 0].tolist()]
                return new_options, sat if sat else ""
            except Exception as e:
                print(f"Error fetching or reading CSV for channels: {e}")
                return [], ""
        else:
            try:
                default_options = utilities.populate_inputs(
                    AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY)
                return default_options, sat
            except Exception as e:
                print(f"Error populating default inputs: {e}")
                return [], sat
    elif trigger_id == 'sat-dropdown':
        return dash.no_update, sat if sat else "Galaxy 30"

@app.callback(
    Output(component_id="celestrak-output", component_property="children"),
    [
        Input(
            component_id="button-update-celestrak",
            component_property="n_clicks",
        )
    ], suppress_callback_exceptions=True
)



def update_celestrak_tles(click: int):
    """
    Callback to run file to pull and write CelesTrak TLEs to the AWS bucket.

    Parameters
    ----------
    click: int
        Integer representing if the button is clicked.
    """
    changed_ids = [property["prop_id"] for property in dash.callback_context.triggered][0]
    if click and "button-update-celestrak" in changed_ids:
        get_celestrak_data()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return "TLEs successfully pulled: " + str(now)
    return ""



@app.callback(
    Output(component_id="tabs-content", component_property="children"),
    [
        Input(component_id="tabs", component_property="value"),
        Input(component_id="sat-dropdown", component_property="value"),
    ], suppress_callback_exceptions=True
)
def render_content(tab: str, value: str, aws_client=AWS_CLIENT, aws_bucket=AWS_BUCKET_NAME):
    """
    Callback to render tab content.

    Parameters
    ----------
    search: str
        String containing valid search option chosen in search bar/dropdown.
    tab: str
        String containing chosen tab.
    """

    source_path = f"satbeams.csv"
    does_exist = utilities.prefix_exists(aws_client, aws_bucket, source_path)
    if does_exist:
        obj = (
            aws_client.get_object(Bucket=aws_bucket, Key=source_path)["Body"]

        )
        df = pd.read_csv(obj, header=0)

        if value in df.iloc[:, 0].values:
            df_subset = df[df.iloc[:, 0] == value]
            norad = df_subset.iloc[0, 3]
        else:
            norad = "none"

    if tab == "tab-general":
        return populate_utilities.populate_general_info(
            AWS_CLIENT, AWS_BUCKET_NAME, value, norad, PATH_KEY
        )
    if tab == "tab-telemetry":
        return populate_utilities.populate_tles(AWS_CLIENT, AWS_BUCKET_NAME, norad, PATH_KEY)
    if tab == "tab-footprints":
        return populate_utilities.populate_footprints(
            AWS_CLIENT, AWS_BUCKET_NAME, value,norad, PATH_KEY
        )
    if tab == "tab-freq_plans":
        return populate_utilities.populate_freq_plans(
            AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY
        )
    if tab == "tab-channels":
        return populate_utilities.populate_channels(
            AWS_CLIENT, AWS_BUCKET_NAME, value,norad, PATH_KEY
        )
    if tab == "tab-dishpointer":
        return populate_utilities.update_lat_long_and_calculate(1,latitude=0, longitude=0, aws_client=AWS_CLIENT, aws_bucket=AWS_BUCKET_NAME, norad=norad, key=PATH_KEY)
    return ""



@app.callback(
    Output(component_id="data-table", component_property="data"),
    [
        Input(component_id="sat-dropdown", component_property="value"),
    ],suppress_callback_exceptions=True,
)
def update_rows( sat: str):
    """
    Callback to update datatable dependent on filter values.

    Parameters
    ----------
    column: str
        String containing chosen column filter.
    value: str
        String containing chosen filter by value.
    sat: str
        String containing valid search option chosen in search bar/dropdown.
    """
    try:
        file_name = f"channels/{sat}/{sat}.csv"
        obj = AWS_CLIENT.get_object(Bucket=AWS_BUCKET_NAME, Key=file_name)
        df = pd.read_csv(obj['Body'])
    except Exception as e:
        return []
    return df.to_dict("records")


@app.callback(
    [
        Output("latitude-input", "value"),
        Output("longitude-input", "value"),
        Output("azimuth-text", "children"),
        Output("elevation-text", "children"),
        Output("map-frame", "src")
    ],
    [
        Input("button-update", "n_clicks"),
        Input("tabs", "value"),
        Input("sat-dropdown", "value"),
    ],
    [
        dash.State("latitude-input", "value"),
        dash.State("longitude-input", "value"),
        dash.State("location-input", "value"),
        
    ],
    suppress_callback_exceptions=True,
)
def update_map(n_clicks, value, satellite,latitude, longitude, location):
    """
    Callback to update the map, azimuth, and elevation when the button is clicked or tab is switched.
    
    Parameters
    ----------
    n_clicks: int
        Number of times the button has been clicked.
    active_tab: str
        ID of the active tab.
    latitude: float
        Latitude for the dish pointer.
    longitude: float
        Longitude for the dish pointer.
    satellite: str
        Satellite selected from the dropdown.
    """
    
    global CURRENT_LOCATION
    try:
        if n_clicks or value == "tab-dishpointer" or satellite or CURRENT_LOCATION:
            if location:
                latitude, longitude = utilities.get_location_data(location)
            if satellite:
                source_path = "satbeams.csv"  # Adjust as per your setup
                does_exist = utilities.prefix_exists(
                    AWS_CLIENT, AWS_BUCKET_NAME, source_path)

                if does_exist:
                    obj = AWS_CLIENT.get_object(
                        Bucket=AWS_BUCKET_NAME, Key=source_path)["Body"]
                    df = pd.read_csv(obj, header=0)

                    if satellite in df.iloc[:, 0].values:
                        df_subset = df[df.iloc[:, 0] == satellite]
                        norad = df_subset.iloc[0, 3]
                        
                        
                        if CURRENT_LOCATION == 1:
                            ipinfo_handler = ipinfo.getHandler(access_token)
                            details = ipinfo_handler.getDetails()
                            latitude = details.latitude
                            longitude = details.longitude
                            CURRENT_LOCATION = 0

                        map_src = f"https://www.google.com/maps/embed/v1/place?key={
                            API_KEY}&q={latitude},{longitude}"
                        
                        azimuth, elevation = dish_pointer(
                            aws_client=AWS_CLIENT,  # Replace with actual AWS client
                            aws_bucket=AWS_BUCKET_NAME,  # Replace with your AWS bucket name
                            norad=norad,  # Replace with the NORAD ID
                            latitude=latitude,
                            longitude=longitude,
                        )
                        # Check if azimuth and elevation are within valid ranges
                        if (azimuth > 360 or azimuth < 0) or (elevation > 90 or elevation < 0):
                            azimuth_text = "IMPOSSIBLE TO REACH SATELLITE"
                            elevation_text = "Azimuth: {:.2f}°, Elevation: {:.2f}°".format(
                                azimuth, elevation)
                        else:
                            azimuth_text = f"Azimuth: {azimuth:.2f}°"
                            elevation_text = f"Elevation: {elevation:.2f}°"
                        
                        return latitude, longitude, azimuth_text, elevation_text, map_src

        return latitude, longitude, "", "", ""
    except Exception as e:
        return latitude, longitude, "", "", ""






if __name__ == "__main__":
    app.run_server(debug=True)