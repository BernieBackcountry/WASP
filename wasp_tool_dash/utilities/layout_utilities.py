"""
This module defines functions for creating dynamic Dash layout components that
are populated via Dash callbacks.

FUNCTIONS
    def create_column_filter() -> dcc.Dropdown:
        Create column filter dropdown for the channels tab.
    def create_value_filter() -> dcc.Dropdown:
        Create dropdown containing filter by options for the channels tab.
    def create_data_table(df: pd.DataFrame) -> dash_table.DataTable:
        Create Dash datatable for the channels tab.
"""
import pandas as pd
from dash import dash_table, dcc


def create_column_filter() -> dcc.Dropdown:
    """
    Create column filter dropdown for the channels tab.

    Returns
    -------
    dcc.Dropdown
        Unpopulated dropdown for column filter options

    """
    return dcc.Dropdown(
        ["Channel Status", "Ku/C-band"],
        id="column-filter",
        placeholder="Filter by...",
        style={"marginLeft": "5px", "maxWidth": "300px"},
    )


def create_value_filter() -> dcc.Dropdown:
    """
    Create dropdown containing filter by options for the channels tab.

    Returns
    -------
    dcc.Dropdown
        Unpopulated dropdown for filter by options

    """
    return dcc.Dropdown(
        id="value-filter", style={"marginLeft": "5px", "maxWidth": "300px"}
    )


def create_data_table(df: pd.DataFrame) -> dash_table.DataTable:
    """
    Create Dash datatable for the channels tab.

    Returns
    -------
    dash_table.DataTable
        Unpopulated datatable.
    """
    return dash_table.DataTable(
        df.to_dict("records"),
        [{"name": i, "id": i} for i in df.columns],
        id="data-table",
        sort_action="native",
        style_cell={"fontSize": 14, "textAlign": "left"},
        style_header={"backgroundColor": "grey", "fontWeight": "bold"},
        style_data_conditional=[
            {
                "if": {
                    "column_id": "Ku/C-band",
                },
                "display": "None",
            }
        ],
        style_header_conditional=[
            {
                "if": {
                    "column_id": "Ku/C-band",
                },
                "display": "None",
            }
        ],
    )
