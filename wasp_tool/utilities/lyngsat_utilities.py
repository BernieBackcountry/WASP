"""
This module pulls satellite channel information and channel status from lyngsat.com

FUNCTIONS
    def prepare_lyngsat() -> Tuple[dict, dict]:
        Generates a dictionary containing all satellites primary and secondary names pulled
        from LyngSat.
        Generates a dictionary of processed and refactored tables containing channel
        information and status for each satellite.
    def get_region_urls() -> list:
        Generates a list of urls for each region in REGIONS (pre-defined constant).
    def get_satellite_urls(region_urls: list) -> dict:
        Generates a dictionary of all satellite names and urls.
    def find_hrefs(soup: BeautifulSoup) -> dict:
        Find all hrefs within parsed html text.
    def clean_hrefs(hrefs_dict: dict) -> dict:
        Remove extraneous hrefs from a dict of satellite hrefs.
    def get_satellite_names(satellite_urls_dict: dict) -> dict:
        Generates dictionary containing primary and secondary names for each satellite.
    def get_satellite_html_tables(satellite_url_dict: dict, satellite_names_dict: dict) -> dict:
        Generates a dictionary of all html tables for each satellite.
    def convert_html_tables_to_dataframes(html_tables: dict) -> dict:
        Convert parsed html tables into pandas dataframes.
    def read_multirow_table_into_standard_format(
        table_rows: list, num_rows: int
    ) -> pd.DataFrame:
        Reads in and converts a html text table into a pandas dataframe format.
    def replace_breaks_with_newlines(table: str) -> str:
        Replace breaks in html text with newline characters.
    def get_row_spans(cell: str) -> int:
        Determine the multi-row span for a given table cell.
    def denote_italicized_table_entries_with_asterik(
        table_df: pd.DataFrame,
        table_cell: str,
        index: int,
        column_index: int,
        column_width: int,
        rows_per_cell: int,
    ) -> pd.DataFrame:
        Denotes italicized entries in html text by adding an '*' to string text.
    def clean_all_dataframes(satellite_df_tables_dict: dict) -> dict:
        Resize multirow entries to new columns and clean all pd.DataFrame type tables.
    def split_frequency_beam_and_eirp_values(
        df_subset: pd.DataFrame, df_new: pd.DataFrame
        ) -> pd.DataFrame:
        Split multi-row frequency/beam/eirp values into separate dataframe columns.
    def split_system_sr_and_fec_values(
        df_subset: pd.DataFrame, df_new: pd.DataFrame
    ) -> pd.DataFrame:
        Split multi-row system/fr/fec values into separate dataframe columns.
    def edit_provider_name_and_channel_name_values(
        df_subset: pd.DataFrame, df_new: pd.DataFrame
    ) -> pd.DataFrame:
        Refactor provider name/channel name values into new format.
    def determine_channel_status(
        satellite_html_tables_dict: dict, satellite_df_tables_clean_dict: dict
    ) -> dict:
        Determine channel status and add new column to cleaned df tables.
    def remove_empty_tables(html_tables: list, df_tables: list) -> Tuple[list, list]:
        Remove empty tables from lists.
    def clean_provider_channel_name_rows(table: pd.DataFrame) -> pd.DataFrame:
        Remove extraneous values from the (Provider) Channel Name column.
    def create_bands_column(df_org: pd.DataFrame) -> pd.DataFrame:
        Creates the Ku/C-band column.
"""

import sys
from typing import Tuple

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from wasp_tool import utilities

pd.options.mode.chained_assignment = None  # default='warn'

LYNGSAT_HOMEPAGE = "https://www.lyngsat.com/"

# define categories on Lyngsat homepage
REGIONS = ["Asia", "Europe", "Atlantic", "America"]

# define http response success
HTTP_SUCCESS = 200

# define number of table columns for each satellite page
NUM_COLS = 10


def prepare_lyngsat() -> Tuple[dict, dict]:
    """
    Generates a dictionary containing all satellites primary and secondary names pulled
    from LyngSat.

    Generates a dictionary of processed and refactored tables containing channel
    information and status for each satellite.

    Returns
    -------
    Tuple[dict, dict]

    satellite_names_dict: dict
        Dictionary containing all satellite primary and secondary names.

    satellite_df_tables_final_dict: dict
        Dictionary containing process and refactored channel table for each satellite.
    """
    # get region urls
    region_urls = get_region_urls()
    # get all satellite urls
    satellite_urls_dict = get_satellite_urls(region_urls)
    # get primary and secondary satellite names in dict
    satellite_names_dict = get_satellite_names(satellite_urls_dict)
    # get dict of all html tables for all satellites
    satellite_html_tables_dict = get_satellite_html_tables(
        satellite_urls_dict, satellite_names_dict
    )
    # convert the html tables to pd dataframes
    satellite_df_tables_dict = convert_html_tables_to_dataframes(
        satellite_html_tables_dict
    )
    # clean each df table
    satellite_df_tables_clean_dict = clean_all_dataframes(satellite_df_tables_dict)
    # determine channel status for each channel in all tables
    satellite_df_tables_final_dict = determine_channel_status(
        satellite_html_tables_dict, satellite_df_tables_clean_dict
    )
    return satellite_names_dict, satellite_df_tables_final_dict


def get_region_urls() -> list:
    """
    Generates a list of urls for each region in REGIONS (pre-defined constant).

    Returns
    -------
    region_urls: list
        List containing corresponding url for each region
    """
    http_response = requests.get(LYNGSAT_HOMEPAGE)
    if http_response.status_code == HTTP_SUCCESS:
        soup = BeautifulSoup(http_response.text, "lxml")
        region_urls = []
        for region in REGIONS:
            url = str(soup.find("a", text=region, href=True)["href"])
            full_url = LYNGSAT_HOMEPAGE + url
            region_urls.append(full_url)
        return region_urls
    print("Unsuccessful HTTP request at ", LYNGSAT_HOMEPAGE)
    print("Exiting script...")
    sys.exit()


def get_satellite_urls(region_urls: list) -> dict:
    """
    Generates a dictionary of all satellite names and urls.

    Returns
    -------
    satellite_url_dict: dict
        Dictionary containing satellite names and corresponding urls.
    """
    satellite_url_dict = {}
    for region in region_urls:
        response = requests.get(
            region, allow_redirects=False
        )  # Heroku has specified timeout
        # Check if the status_code is 200
        if response.status_code == HTTP_SUCCESS:
            # Parse the HTML content of the webpage
            soup = BeautifulSoup(response.content, "lxml")
            # Find hrefs
            hrefs_dict = find_hrefs(soup)
            # Clean hrefs dict
            hrefs_dict_clean = clean_hrefs(hrefs_dict)
            # Convert href to full urls
            for k, val in hrefs_dict_clean.items():
                satellite_url_dict[k] = "https://www.lyngsat.com/" + val
    return satellite_url_dict


def find_hrefs(soup: BeautifulSoup) -> dict:
    """
    Find all hrefs within parsed html text.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text.

    Returns
    -------
    hrefs_dict: dict
        Dictionary containing all hrefs on a page. For each entry, the href.text
        is the key and the href is the value
    """
    hrefs_dict = {}
    # create dictionary with href as value and satellite name as key
    for href in soup.find_all("a", href=True):
        hrefs_dict[href.text] = href["href"]
    return hrefs_dict


def clean_hrefs(hrefs_dict: dict) -> dict:
    """
    Remove extraneous hrefs from a dict of satellite hrefs.

    Parameters
    ----------
    hrefs_dict: dict
        Dictionary of hrefs to satellite subpages

    Returns
    -------
    clean_hrefs_dict: dict
        Dictionary of hrefs to satellite subpages without extraneous values
    """
    # remove extraneous href entries
    temp_dict = dict(
        [
            (k, val)
            for k, val in hrefs_dict.items()
            if "http" not in val and "and" not in val
        ]
    )
    # remove repeat entries with incorrect key values
    clean_hrefs_dict = dict([(k, val) for k, val in temp_dict.items() if "." not in k])
    return clean_hrefs_dict


def get_satellite_names(satellite_urls_dict: dict) -> dict:
    """
    Generates dictionary containing primary and secondary names for each satellite.

    Parameters
    ----------
    satellite_urls_dict: dict
        Dictionary containing satellite names and corresponding urls
    Returns
    -------
    satellite_names_dict: dict
        Dictionary containing all primary and secondary satellite names
    """
    primary_satellite_names = []
    secondary_satellite_names = []
    # loop through each satellite href
    for key in satellite_urls_dict.keys():
        delimiter = "("
        if delimiter in key:
            temp = key.split(delimiter, maxsplit=1)
            primary_satellite_name = utilities.standardize_satellite(temp[0])
            primary_satellite_names.append(primary_satellite_name)
            secondary_satellite_name = utilities.standardize_satellite(temp[1])
            secondary_satellite_names.append(secondary_satellite_name)
        else:
            primary_satellite_name = utilities.standardize_satellite(key)
            primary_satellite_names.append(primary_satellite_name)
            secondary_satellite_names.append("")

    satellite_names_dict = {
        "Primary Satellite Name": primary_satellite_names,
        "Secondary Satellite Name(s)": secondary_satellite_names,
    }

    return satellite_names_dict


def get_satellite_html_tables(
    satellite_url_dict: dict, satellite_names_dict: dict
) -> dict:
    """
    Generates a dictionary of all html tables for each satellite.

    Parameters
    ----------
    satellite_url_dict: dict
        Dictionary containing satellite names and corresponding urls

    satellite_names_dict: dict
        Dictionary containing all primary and secondary satellite names

    Returns
    -------
    html_tables_dict: dict
        Dictionary containing all html tables for each satellite
        key: satellite's primary name
        value: list of html tables
    """
    html_tables_dict = {}
    satellite_primary_names = satellite_names_dict["Primary Satellite Name"]
    count = 0
    for key, value in satellite_url_dict.items():
        # Define max attempts for each requests.get
        maximum_attempts = 10
        for i in range(maximum_attempts):
            try:
                http_response = requests.get(value)  # Heroku has specified timeout
                # Check if the status_code is 200
                if http_response.status_code == 200:
                    # Parse the HTML content of the webpage
                    soup = BeautifulSoup(http_response.content, "lxml")
                    html_tables = []
                    for table in soup.find_all("table"):
                        text = table.text
                        # smart search for table of interest, no class or tags to search by
                        string_check = "https://www.lyngsat.com/"
                        if string_check in text:
                            # only the bigtable has a class
                            if not table.has_attr("class"):
                                html_tables.append(table)
                    entry = satellite_primary_names[count]
                    html_tables_dict[entry] = html_tables
                    # print("Attempt", i + 1, "successful for", key)
                    break
            except:
                print("Attempt", i + 1, "unsuccessful for", key)
        count += 1
    return html_tables_dict


def convert_html_tables_to_dataframes(html_tables: dict) -> dict:
    """
    Convert parsed html tables into pandas dataframes.

    Parameters
    ----------
    html_dict: dict
        Dictionary containing all html tables for each satellite
        key: satellite's primary name
        value: list of html tables

    Returns
    -------
    satellite_df_tables_dict: dict
        Dictionary containing all pd.DataFrame tables for each satellite
        key: satellite's primary name
        value: list of pd.DataFrame tables
    """
    satellite_df_tables_dict = {}
    for key, html_tables in html_tables.items():
        list_of_tables = []
        for table in html_tables:
            # replace table breaks with new lines
            table = replace_breaks_with_newlines(table)

            table_rows = table.find_all("tr")
            num_rows = len(table_rows)

            # read multi-row table
            df_table = read_multirow_table_into_standard_format(table_rows, num_rows)

            list_of_tables.append(df_table)
        satellite_df_tables_dict[key] = list_of_tables
    return satellite_df_tables_dict


def replace_breaks_with_newlines(table: str) -> str:
    """
    Replace breaks in html text with newline characters.

    Parameters
    ----------
    table: str
        String containing html text for a given html table

    Returns
    -------
    table: str
        String String containing html text for a given html table with newline
        characters instead of break elements
    """
    for br in table.find_all("br"):
        br.replace_with("\n")
    return table


def read_multirow_table_into_standard_format(
    table_rows: list, num_rows: int
) -> pd.DataFrame:
    """
    Reads in and converts a html text table into a pandas dataframe format.

    Parameters
    ----------
    tables_rows: str
        List containing html text representing each row in the table
    num_rows: int
        Number of table rows

    Returns
    -------
    df: pd.DataFrame
        Dataframe respresentation of the original html text table

    """
    # instantialize empty df of size num_rows x NUM_COLS
    df = pd.DataFrame(np.ones((num_rows, NUM_COLS)) * np.nan)

    column_width = 1
    # handle multi-row columns
    for index, row in enumerate(table_rows):
        try:
            column_index = df.iloc[index, :][df.iloc[index, :].isnull()].index[0]
        except IndexError:
            print(index, row)

        for cell in row.find_all(["td", "th"]):
            rows_per_cell = get_row_spans(cell)
            # find first non-na col and fill that one
            while any(
                df.iloc[index, column_index : column_index + rows_per_cell].notnull()
            ):
                column_index += 1

            df = denote_italicized_table_entries_with_asterik(
                df, cell, index, column_index, column_width, rows_per_cell
            )

            if column_index < df.shape[1] - 1:
                column_index += column_width

    return df


def get_row_spans(cell: str) -> int:
    """
    Determine the multi-row span for a given table cell.

    Parameters
    ----------
    cell: str
        String containing table cell

    Returns
    -------
    rep_row: int
        Number of rows in the multi-row cell
    """
    if cell.has_attr("rowspan"):
        rep_row = int(cell.attrs["rowspan"])
    else:
        rep_row = 1
    return rep_row


def denote_italicized_table_entries_with_asterik(
    table_df: pd.DataFrame,
    table_cell: str,
    index: int,
    column_index: int,
    column_width: int,
    rows_per_cell: int,
) -> pd.DataFrame:
    """
    Denotes italicized entries in html text by adding an '*' to string text.

    Parameters
    ----------
    table_df: pd.DataFrame
        Dataframe to populate with entries
    table_cell: str
        String containing table cell
    index: int
        Counter
    column_index: int
        Current column index
    column_width: int
        Number of columns in a table
    rows_per_cell: int
        Number of rows per cell in a table
    Returns
    -------
    table_df: pd.DataFrame
        Populated dataframe
    """
    # check if <i> is a child of cell
    children = table_cell.findChildren()
    for child in children:
        # add asterik to signal text was originally in italics; this is key
        # for separating the provider/channel column
        if child.find("i"):
            table_df.iloc[
                index : index + rows_per_cell,
                column_index : column_index + column_width,
            ] = (
                str(table_cell.getText() + "*")
            )
            break
        table_df.iloc[
            index : index + rows_per_cell,
            column_index : column_index + column_width,
        ] = str(table_cell.getText())
    return table_df


def clean_all_dataframes(satellite_df_tables_dict: dict) -> dict:
    """
    Resize multirow entries to new columns and clean all pd.DataFrame type tables.

    Parameters
    ----------
    satellite_df_tables_dict: dict
        Dictionary containing all pd.DataFrame tables for each satellite
        key: satellite's primary name
        value: list of pd.DataFrame tables

    Returns
    -------
    satellite_df_tables_dict_clean: dict
        Dictionary containing all cleaned/resized pd.DataFrame tables for each satellite
        key: satellite's primary name
        value: list of pd.DataFrame tables

    """
    satellite_df_tables_dict_clean = {}
    for key, list_of_dataframes in satellite_df_tables_dict.items():
        list_of_dataframes_clean = []
        for df_table in list_of_dataframes:
            # drop all columns except 0, 1, and 3 corresponding to
            # (0) Frequency Beam EIRP (dBW)
            # (1) System SR FEC
            # (3) Provider Name Channel Name

            # convert all columns to string type
            df_table = df_table.astype(str)

            # create new df with desired column subset
            df_clean = df_table.iloc[:, [0, 1, 3]]
            # drop header and footer rows
            df_clean.drop(
                index=[df_clean.index[0], df_clean.index[1]], axis=0, inplace=True
            )
            df_clean.drop(index=df_clean.index[-1], axis=0, inplace=True)
            df_clean.reset_index(drop=True, inplace=True)

            # instantiate empty dataframe with desired columns
            num_cols = 9
            df_new = pd.DataFrame(
                np.ones((len(df_clean), num_cols)) * np.nan,
                columns=[
                    "(Provider) Channel Name",
                    "Channel Status",
                    "Frequency",
                    "System",
                    "SR",
                    "FEC",
                    "Transponder",
                    "Beam",
                    "EIRP (dBW)",
                ],
            )

            # iterate through rows with same info for col 0 (i.e. identify multirow boundaries)
            rows = df_clean[0].unique()

            for val in rows:
                df_subset = df_clean.loc[df_clean[0].isin([val])]
                # split multirow values into individual columns
                df_new = split_frequency_beam_and_eirp_values(df_subset, df_new)
                df_new = split_system_sr_and_fec_values(df_subset, df_new)
                df_new = edit_provider_name_and_channel_name_values(df_subset, df_new)

            list_of_dataframes_clean.append(df_new)
        satellite_df_tables_dict_clean[key] = list_of_dataframes_clean
    return satellite_df_tables_dict_clean


def split_frequency_beam_and_eirp_values(
    df_subset: pd.DataFrame, df_new: pd.DataFrame
) -> pd.DataFrame:
    """
    Split multi-row frequency/beam/eirp values into separate dataframe columns.

    Parameters
    ----------
    df_subset: pd.DataFrame
        Dataframe containing a single multi-row entry to separate
    df_new: pd.DataFrame
        Dataframe to be populated by function operations

    Returns
    -------
    df_new: pd.DataFrame
        Dataframe with now populated entries
    """
    # split column 0
    col0_value = str(df_subset.iloc[0, 0])
    split0_value = col0_value.split("\n")
    for split in split0_value:
        if "tp" in split:
            df_new.loc[df_subset.index, "Transponder"] = str(split)
            continue
        if any(s.isdigit() for s in split) is False:
            df_new.loc[df_subset.index, "Beam"] = str(split)
            continue
        if ("L" in split) or ("R" in split) or ("H" in split) or ("V" in split):
            df_new.loc[df_subset.index, "Frequency"] = str(split)
            continue
        if "*" in split:
            split = split.replace("*", "")
            df_new.loc[df_subset.index, "EIRP (dBW)"] = str(split)
    return df_new


def split_system_sr_and_fec_values(
    df_subset: pd.DataFrame, df_new: pd.DataFrame
) -> pd.DataFrame:
    """
    Split multi-row system/fr/fec values into separate dataframe columns.

    Parameters
    ----------
    df_subset: pd.DataFrame
        Dataframe containing a single multi-row entry to separate
    df_new: pd.DataFrame
        Dataframe to be populated by function operations

    Returns
    -------
    df_new: pd.DataFrame
        Dataframe with now populated entries
    """
    # split column 1
    col1_value = str(df_subset.iloc[0, 1])
    split1_value = col1_value.split("\n")
    for split in split1_value:
        if "/" in split:
            df_new.loc[df_subset.index, "FEC"] = split
            continue
        elif all(s.isdigit() for s in split):
            df_new.loc[df_subset.index, "SR"] = split
            continue
        else:
            if df_new.loc[df_subset.index, "System"].isnull().values.all():
                df_new.loc[df_subset.index, "System"] = split
            else:
                df_new.loc[df_subset.index, "System"] = (
                    df_new.loc[df_subset.index, "System"].astype(str) + " " + split
                )
    return df_new


def edit_provider_name_and_channel_name_values(
    df_subset: pd.DataFrame, df_new: pd.DataFrame
) -> pd.DataFrame:
    """
    Refactor provider name/channel name values into new format.

    Parameters
    ----------
    df_subset: pd.DataFrame
        Dataframe containing a single multi-row entry to separate
    df_new: pd.DataFrame
        Dataframe to be populated by function operations

    Returns
    -------
    df_new: pd.DataFrame
        Dataframe with now populated entries
    """
    # split column 2
    new_string = ""
    for i in range(0, len(df_subset)):
        test_string = str(df_subset.iloc[i, 2])
        if "*" in test_string:
            new_string = test_string.replace("*", "")
            df_new.loc[df_subset.index, "(Provider) Channel Name"] = (
                "(" + new_string + ")"
            )
        else:
            if new_string == "":
                df_new.loc[df_subset.index[i], "(Provider) Channel Name"] = test_string
            else:
                df_new.loc[df_subset.index[i], "(Provider) Channel Name"] = (
                    "(" + new_string + ") " + test_string
                )
    return df_new


def determine_channel_status(
    satellite_html_tables_dict: dict, satellite_df_tables_clean_dict: dict
) -> dict:
    """
    Determine channel status and add new column to cleaned df tables.

    Parameters
    ----------
    satellite_html_tables_dict: dict
        Dictionary containing all html tables for each satellite
        key: satellite's primary name
        value: list of html tables
    satellite_df_tables_clean_dict: dict
        Dictionary containing all cleaned/resized pd.DataFrame tables for each satellite
        key: satellite's primary name
        value: list of pd.DataFrame tables

    Returns
    -------
    satellite_df_tables_new_dict: dict
        Dictionary containing one master channels table per satellite
        key: satellite's primary name
        value: list of pd.DataFrame tables
    """
    yellow = "background:#ffffbb"
    green = "background:#bbffbb"

    satellite_df_tables_new_dict = {}

    for key, df_table_list in satellite_df_tables_clean_dict.items():
        # note the two input dicts have matching keys
        html_table_list = satellite_html_tables_dict[key]
        # remove empty tables
        html_tables, df_tables = remove_empty_tables(html_table_list, df_table_list)

        # TODO: Determine why this is the only page breaking
        if "EUTELSAT 113 WEST A" in key:
            continue

        # check for empty list after removing empty tables
        if df_tables:
            # get html for Provider Name/Channel Name column to determine channel status
            html_columns = []
            for html_table in html_tables:
                col_entries = []
                # get table rows
                rows = html_table.find_all("tr")
                # for each row grab column entry cell
                for row in rows:
                    cell = row.find_all("td")
                    # header/footer condition
                    if len(cell) > 1:
                        # cond for multirow
                        if len(cell) == 8:
                            col_entries.append(cell[1])
                        # cond for singular row
                        elif len(cell) == 10:
                            col_entries.append(cell[3])
                # drop first entry as it is column name
                html_columns.append(col_entries[1:])

            # loop through html columns
            for h, col in enumerate(html_columns):
                table_star = df_tables[h]
                # loop through channel name values in a given table
                for m in range(0, len(table_star["(Provider) Channel Name"].values)):
                    if 0 <= m < len(col):
                        cell = col[m]
                    else:
                    # Handle the out-of-range case
                     print("Index out of range.")
                    channel_status = cell["style"]
                    if (channel_status == green) or (channel_status == yellow):
                        table_star.loc[m, "Channel Status"] = str("ON")
                    else:
                        table_star.loc[m, "Channel Status"] = str("OFF")

            # combine all tables into one large one
            master_table = pd.concat(df_tables, ignore_index=True)
            # drop excess rows
            master_table_clean = clean_provider_channel_name_rows(master_table)
            # create ku/c-band column
            master_table_new = create_bands_column(master_table_clean)
            # add final table to new dict
            satellite_df_tables_new_dict[key] = master_table_new
    return satellite_df_tables_new_dict


def remove_empty_tables(html_tables: list, df_tables: list) -> Tuple[list, list]:
    """
    Remove empty tables from lists.

    Parameters
    ----------
    html_tables: list
        List of html text tables for a given satellite
    df_tables: list
        List of dataframe tables for a given satellite

    Returns
    -------
    html_tables: list
        List of html text tables for a given satellite with no empty tables
    df_tables: list
        List of dataframe tables for a given satellite with no empty tables
    """
    # determine empty tables to drop
    empty_indicies = []
    for index, table in enumerate(df_tables):
        if table.empty:
            empty_indicies.append(index)

    for ind in empty_indicies:
        html_tables.pop(ind)
        df_tables.pop(ind)

    return html_tables, df_tables


def clean_provider_channel_name_rows(table: pd.DataFrame) -> pd.DataFrame:
    """
    Remove extraneous values from the (Provider) Channel Name column.

    Parameters
    ----------
    table: pd.DataFrame
        Dataframe to edit.
    Returns
    -------
    tabble: pd.DataFrame
        Editted dataframe.
    """
    # drop blank/unnecessary rows based on provider/channel condition
    drop = []
    for row in range(len(table)):
        row_val = table["(Provider) Channel Name"].iloc[row]
        # check for \n rows
        if "\n" in str(row_val):
            drop.append(row)
        # check for NaN rows
        if pd.isnull(row_val):
            drop.append(row)
        # check for provider only rows
        value = row_val.strip()
        if (value.rfind("(") == 0) and (value.rfind(")") == (len(value) - 1)):
            drop.append(row)
        # can add something to check for feeds etc.
        if value in ["test card", "info card", "feeds"]:
            drop.append(row)

    table.drop(drop, axis=0, inplace=True)
    return table


def create_bands_column(df_org: pd.DataFrame) -> pd.DataFrame:
    """
    Creates the Ku/C-band column.

    Parameters
    ----------
    df_org: pd.DataFrame
        Dataframe to edit.
    Returns
    -------
    df_org: pd.DataFrame
        Editted dataframe.
    """
    df_org["Ku/C-band"] = np.nan
    for k, entry in enumerate(df_org["Frequency"]):
        # check for empty entry
        if not pd.isnull(entry):
            res = "".join([ele for ele in entry if ele.isdigit()])
            if int(res) > 9999:
                df_org.loc[k, "Ku/C-band"] = str("Ku-band")
            else:
                df_org.loc[k, "Ku/C-band"] = str("C-band")
    return df_org
