"""
This module pulls TLE data from celestrak.org for all active geosynchronous satellites.

FUNCTIONS
    prepare_celestrak()
        Generates a dictionary containing all satellites primary names, secondary names, and TLE
        data pulled from CelesTrak.
    get_tles(html_text: list)
        Extracts primary satellite name, secondary satellite name(s), and TLEs from the given
        html text.
    def create_data_dictionary(primary_sat_names: list, secondary_sat_names: list, tles: list)
        Create data dictionary from a given set of lists.
"""
import sys

import numpy as np
import requests

from wasp_tool import utilities

CELESTRAK_HOMEPAGE = "https://celestrak.com/NORAD/elements/geo.txt"

# define http response success
HTTP_SUCCESS = 200


def prepare_celestrak() -> dict:
    """
    Generates a dictionary containing all satellites primary names, secondary names, and TLE data
    pulled from CelesTrak.

    Returns
    -------
    data_dictionary: dict
        Dictionary of lists containing all satellites primary names, secondary names, and TLEs.
    """
    response = requests.get(CELESTRAK_HOMEPAGE)  # Heroku has specified timeout

    if response.status_code == HTTP_SUCCESS:
        html_text = response.text.split("\n")
        celestrak_data = get_tles(html_text)
        return celestrak_data
    print("Unsuccessful HTTP request at ", CELESTRAK_HOMEPAGE)
    print("Exiting script...")
    sys.exit()


def get_tles(html_text: list) -> np.array:
    """
    Extracts primary satellite name, secondary satellite name(s), and TLEs from
    the given html text.

    Parameters
    ----------
    html_text: list
        List containing html text obtained from http request.

    Returns
    -------
    data_dictionary: dict
        Dictionary of lists containing all satellites primary names, secondary names, and TLEs.
    """
    line_count = 3  # every third line break begins TLEs for new sat
    num_satellites = int(len(html_text)/3)
    print("NUM SATS", num_satellites)
    celestrak_data = np.empty((num_satellites, 3, 1), dtype=object)
    print(celestrak_data[0, 0, 0])

    # iterate through lines to get sat names and corresponding TLEs
    index = 0

    for i, line in enumerate(html_text):
        if (i % line_count == 0) and (i <= (len(html_text) - line_count)):
            # separate out TLEs
            tle_line_1 = html_text[i + 1].strip().replace(" ", "*")
            tle_line_2 = html_text[i + 2].strip().replace(" ", "*")

            # separate out satellite names
            sat_names = line.strip()

            # pre-process sat names
            # sat_names = sat_names.replace(")", "")
            # sat_names = sat_names.split("(")
            # sat_names = [elem for elem in sat_names if elem.strip()]

            # TODO Fix doc strings
            celestrak_data[index, 0, 0] = sat_names
            celestrak_data[index, 1, 0] = tle_line_1
            celestrak_data[index, 2, 0] = tle_line_2

            index += 1

    return celestrak_data
