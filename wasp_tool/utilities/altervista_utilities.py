"""
This module pulls satellite frequency plans from frequencyplansatellites.altervista.org

FUNCTIONS
    def prepare_altervista() -> Tuple[dict, list]:
        Generates a dictionary containing all satellites primary and secondary names pulled
        from Altervista.
        Generates a list of urls linking to each satellite's frequency plan PDF.
    def get_satellite_constellation_urls() -> list:
        Generates a list of urls for each satellite constellation subpage.
    def get_frequency_plans(url: str) -> Tuple[list, list, list]:
        For each satellite in a given constellation, appends the primary satellite names,
        secondary satellite name(s), and frequency plan PDF link to separate lists.
    def get_sats(text: str) -> Tuple[str, str]:
        Generates primary and secondary satellite names for a given vehicle based on
        possible text delimiters.
    def split_text(text: str, split_on: str) -> Tuple[str, str]:
        Splits text input to get primary and secondary satellite names for a given vehicle.
"""
import sys
from typing import Tuple
import numpy as np
import requests
from bs4 import BeautifulSoup

#from wasp_tool import utilities

ALTERVISTA_HOMEPAGE = "http://frequencyplansatellites.altervista.org/"

# define http response success
HTTP_SUCCESS = 200


def prepare_altervista() -> Tuple[dict, list]:
    """
    Generates a dictionary containing all satellites primary and secondary names pulled
    from Altervista.

    Generates a list of urls linking to each satellite's frequency plan PDF.

    Returns
    -------
    Tuple[dict, list]

    satellite_dict: dict
        Dictionary containing each satellite's primary and secondary names
    frequency_plans: list
        List of urls linking to frequency plan PDFs
    """
    constellation_urls = get_constellation_urls()
    num_constellations = len(constellation_urls)
    num_satellites, sat_names, freq_plans = get_frequency_plans(constellation_urls)

    print(num_satellites)
    print(len(sat_names))
    print(len(freq_plans))

    altervista_data = np.empty((num_satellites, 2, 1), dtype=object)

    for index in range(num_satellites):
        altervista_data[index, 0, 0] = sat_names[index]
        altervista_data[index, 1, 0] = freq_plans[index]

    return altervista_data


def get_constellation_urls() -> list:
    """
    Generates a list of urls for each satellite constellation subpage.

    Returns
    -------
    urls: list
        List of urls for each satellite constellation subpage
    """
    http_response = requests.get(ALTERVISTA_HOMEPAGE)  # Heroku has specified timeout
    if http_response.status_code == HTTP_SUCCESS:
        soup = BeautifulSoup(http_response.text, "lxml")
        http_response.close()
        sidebar = soup.find("div", id="sidebar")
        urls = []
        for a in sidebar.find_all("a", href=True):
            urls.append(a["href"])
        return urls
    print("Unsuccessful request at ", ALTERVISTA_HOMEPAGE)
    print("Exiting script...")
    sys.exit()


def get_frequency_plans(constellation_urls: list) -> Tuple[list, list, list]:
    """
    For each satellite in a given constellation, appends the primary satellite names,
    secondary satellite name(s), and frequency plan PDF link to separate lists.

    Parameters
    ----------
    url: str
        String containing the url of a given satellite constellation subpage

    Returns
    -------
    Tuple[list, list, list]

    all_primary_sat_names: list
        List of all primary satellite names for each vehicle in a given constellation
    all_secondary_sat_names: list
        List of all secondary satellite names for each vehicle in a given constellation
    all_frequency_plans_urls: list
        List of all frequency plan links for each vehicle in a given constellation
    """
    num_satellites = 0
    sat_names = []
    freq_plans = []

    for url in constellation_urls:
        http_response = requests.get(url)  # Heroku has specified timeout
        if http_response.status_code == HTTP_SUCCESS:
            soup = BeautifulSoup(http_response.text, "lxml")
            http_response.close()
            sidebar = soup.find("div", id="sidebar")

            for a in sidebar.find_all("a", href=True):
                if ".pdf" in a["href"]:
                    num_satellites += 1
                    sat_names.append(a.text)
                    freq_plans.append(a["href"])
            continue
        print("Unsuccessful request at ", url)
        print("Exiting script...")
        sys.exit()
    return num_satellites, sat_names, freq_plans



def get_sats(text: str) -> Tuple[str, str]:
    """
    Generates primary and secondary satellite names for a given vehicle based on
    possible text delimiters.

    Parameters
    ----------
    text: str
        String containing primary and secondary satellite names

    Returns
    -------
    primary_satellite_name: str
        String containing primary satellite name
    secondary_satellite_name: str
        String containing secondary satellite name(s)

    """
    delimiters = ["(", "-->", "-- >", "--", "/"]
    if any(s in text for s in delimiters):
        # set arbitrary initial minimum
        minimum = 1000
        for delim in delimiters:
            if (text.find(delim) != -1) and (text.find(delim) < minimum):
                # update minimum
                minimum = text.find(delim)
                split_by = delim
        primary_satellite_name, secondary_satellite_name = split_text(text, split_by)
    else:
        primary_satellite_name = text
        secondary_satellite_name = ""
    return primary_satellite_name, secondary_satellite_name


def split_text(text: str, split_on: str) -> Tuple[str, str]:
    """
    Splits text input to get primary and secondary satellite names for a given vehicle.

    Parameters
    ----------
    text: str
        String containing primary and secondary satellite names
    split_on: str
        String containing specified delimiter upon which to split the text

    Returns
    -------
    pri: str
        String containing primary satellite name
    sec: str
        String containing secondary satellite name(s)
    """
    text_split = text.split(split_on, maxsplit=1)
    pri = text_split[0]
    sec = text_split[1]
    return pri, sec
