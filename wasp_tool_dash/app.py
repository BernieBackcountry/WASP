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
from config import BUCKET_NAME,KEY,SECRET_KEY

session = boto3.session.Session()

session = boto3.session.Session()

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
app.layout = layout_creator.create_layout()


@app.callback(
    Output(component_id="sat-dropdown", component_property="value"),
    [Input(component_id="sat-dropdown", component_property="options")], suppress_callback_exceptions=True
)

def update_output(value):
    return value

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
    changed_ids = [property["prop_id"] for property in dash.callback_context.triggered][
        0
    ]
    if click and "button-update-celestrak" in changed_ids:
        get_celestrak_data()
        return "TLEs successfully pulled"
    return ""


@app.callback(
    Output(component_id="tabs-content", component_property="children"),
    [
        Input(component_id="tabs", component_property="value"),
        Input(component_id="sat-dropdown", component_property="value"),
    ], suppress_callback_exceptions=True
)
def render_content(tab: str, value: str):
    """
    Callback to render tab content.

    Parameters
    ----------
    search: str
        String containing valid search option chosen in search bar/dropdown.
    tab: str
        String containing chosen tab.
    """
    if tab == "tab-general":
        return populate_utilities.populate_general_info(
            AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY
        )
    if tab == "tab-telemetry":
        return populate_utilities.populate_tles(AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY)
    if tab == "tab-footprints":
        return populate_utilities.populate_footprints(
            AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY
        )
    if tab == "tab-freq_plans":
        return populate_utilities.populate_freq_plans(
            AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY
        )
    if tab == "tab-channels":
        return populate_utilities.populate_channels(
            AWS_CLIENT, AWS_BUCKET_NAME, value, PATH_KEY
        )
    return


@app.callback(
    Output(component_id="value-filter", component_property="value"),
    [Input(component_id="column-filter", component_property="value")],
    suppress_callback_exceptions=True
)
def render_filter_values(column: str):
    """
    Callback to render column filter and filter by values.

    Parameters
    ----------
    column: str
        String containing chosen column filter.
    """
    table_filters = {
        "Channel Status": ["ON", "OFF"],
        "Ku/C-band": ["Ku-band", "C-band"],
    }
    for filter_options, filter_type in table_filters.items():
        if column == filter_type:
            return filter_options
    return []


@app.callback(
    Output(component_id="data-table", component_property="data"),
    [
        Input(component_id="column-filter", component_property="value"),
        Input(component_id="value-filter", component_property="value"),
        Input(component_id="sat-dropdown", component_property="value"),
    ],suppress_callback_exceptions=True,
)
def update_rows(column: str, value: str, sat: str):
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
    channels_path = f"{sat}.csv"
    df = pd.read_csv(channels_path, header=0)
    if column and value and sat:
        df_subset = df[df[column] == value]
        return df_subset.to_dict("records")
    return df.to_dict("records")




if __name__ == "__main__":
    app.run_server(debug=True)
