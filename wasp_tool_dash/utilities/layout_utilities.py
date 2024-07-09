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



def create_data_table(df: pd.DataFrame) -> dash_table.DataTable:
    """
    Create Dash datatable for the channels tab.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing your data

    Returns
    -------
    dash_table.DataTable
        Unpopulated datatable with filtering options.
    """
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        id="data-table",
        sort_action="native",
        filter_action="native",  
        style_cell={"fontSize": 14, "textAlign": "left"},
        style_header={"backgroundColor": "grey",
                      "fontWeight": "bold", "textAlign": "center"},
        style_filter={'fontWeight': 'bold', 'height': '60px',},
        style_data={'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                    'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        filter_options={'case': 'sensitive', 'operator': 'and', 'trim': True, 'ignoreAccent': False, 'placeholder': 'Filter...'},
    
    )
