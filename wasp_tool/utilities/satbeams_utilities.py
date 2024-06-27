"""
This module pulls general satellite information and footprint images from satbeams.org for all
active geostationary orbits.

FUNCTIONS
    prepare_satbeams()
        Generates a data dictionary containing all satellites primary names, secondary names,
        positions, norad ids, and beacon information.
        Generates a footprint list containing all satellites footprint image links.
    get_active_geostationary_satellite_urls(soup: BeautifulSoup)
         Generates a list of urls for all active geostationary satellites.
    def run_threads(satellite_urls: list) -> Tuple[dict, list]:
        Uses the threading module to run code concurrently reducing overall runtime.
        Threads are used to fetch general information and footprint images for each
        satellite.
    def fetch_data_from_url(
        url: str,
        queue_for_information: queue.Queue,
        queue_for_footprints: queue.Queue
    ):
        Thread wrapper for running functions to obtain general satellite information and
        footprint images.
    def get_satellite_information(soup: BeautifulSoup) -> list:
        Generates a list of information for a given satellite including primary and
        secondary names, position, NORAD ID, and beacon data.
    def find_by_label(soup: BeautifulSoup, label: str) -> str:
        Find the next node that comes after a specified HTML node.
    def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
        Find the first tag that comes after a given HTML tag.
    def get_satellite_footprints(soup: BeautifulSoup) -> list:
        Generates list of footprint images and image titles.
    def list_to_dict(information: list) -> dict:
        Convert list of lists to dictionary.
"""
import queue
import sys
import threading
import time
from typing import Tuple

import requests
from bs4 import BeautifulSoup

from wasp_tool import utilities

SATBEAMS_HOMEPAGE = "https://satbeams.com/satellites?status=active"

# define http response success
HTTP_SUCCESS = 200


def prepare_satbeams() -> Tuple[dict, list]:
    """
    Generates a data dictionary containing all satellites primary names, secondary names, positions,
    norad ids, and beacon information.

    Generates a footprint list containing all satellites footprint image links.

    Returns
    -------
    data_dictionary: dict
        Dictionary of lists containing all satellites primary names, secondary names, positions,
        norad ids, and beacon information.
    footprint_urls:
        List of links to each satellite's footprint images
    """
    response = requests.get(SATBEAMS_HOMEPAGE)  # Heroku has specified timeout
    if response.status_code == HTTP_SUCCESS:
        soup = BeautifulSoup(response.text, "html.parser")
        # get all urls
        all_satellite_urls = get_active_geostationary_satellite_urls(soup)
        # extract information from all urls
        data_dictionary, footprint_urls = run_threads(all_satellite_urls)
        return data_dictionary, footprint_urls
    print("Unsuccessful HTTP request at ", SATBEAMS_HOMEPAGE)
    print("Exiting script...")
    sys.exit()


def get_active_geostationary_satellite_urls(soup: BeautifulSoup) -> list:
    """
    Generates a list of urls for all active geostationary satellites.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text.

    Returns
    -------
    urls: list
        List of urls for all active geostationary satellites.
    """
    urls = []
    for link in soup.findAll("a", {"class": "link"}):
        href = str(link["href"])
        urls.append(f"https://satbeams.com{href}")
    return urls


def run_threads(satellite_urls: list) -> Tuple[dict, list]:
    """
    Uses the threading module to run code concurrently reducing overall runtime.

    Threads are used to fetch general information and footprint images for each
    satellite.

    Parameters
    ----------
    satellite_urls: list
        List of urls for all active geostationary satellites.

    Returns
    -------
    data_dictionary, footprints: Tuple[dict, list]

    data_dictionary: dict
        Dictionary of lists containing all satellites primary names, secondary names, positions,
        norad ids, and beacon information.
    footprints: list
        List of footprint image urls.
    """
    information_queue = queue.Queue()
    footprints_queue = queue.Queue()

    jobs = []
    # create threads
    for satellite_url in satellite_urls:
        thread = threading.Thread(
            target=fetch_data_from_url, args=(satellite_url, information_queue, footprints_queue)
        )
        jobs.append(thread)

    satellite_information = []
    satellite_footprints = []
    # run threads
    for job in jobs:
        # Heroku has a max thread limit so set an arbitrary one
        max_thread = 4
        active_threads = threading.active_count()
        # limit active thread count
        while active_threads > max_thread:
            time.sleep(5)
            active_threads = threading.active_count()
        job.start()
        # get satellite information from queue
        information = information_queue.get()
        satellite_information.append(information)
        # get satellite footprints from queue
        footprints = footprints_queue.get()
        if footprints is None:
            # append empty nested list for None footprints case
            footprints_placeholder_value = [[] for _ in range(2)]
            satellite_footprints.append(footprints_placeholder_value)
        else:
            satellite_footprints.append(footprints)
    for job in jobs:
        job.join()

    satellite_information_dict = list_to_dict(satellite_information)
    return satellite_information_dict, satellite_footprints


def fetch_data_from_url(
    url: str, queue_for_information: queue.Queue, queue_for_footprints: queue.Queue
):
    """
    Thread wrapper for running functions to obtain general satellite information and
    footprint images.

    Parameters
    ----------
    url: str
        String containing url to send GET request to.
    queue_for_information: queue.Queue
        Queue to put general satellite information onto.
    queue_for_footprints: queue.Queue
        Queue to put satellite footprint image urls onto.
    """
    # Define max number of attempts for each requests.get
    attempts = 5
    for i in range(attempts):
        try:
            response = requests.get(url)  # Heroku has specified timeout
            # Check if the status_code is 200
            if response.status_code == HTTP_SUCCESS:
                print("Attempt", i + 1, "successful at", url)
                # Parse the HTML content of the webpage
                soup = BeautifulSoup(response.content, "html.parser")
                # Scrap satellite info
                information = get_satellite_information(soup)
                # Put satellite information on queue
                queue_for_information.put(information)
                # Scrap footprints
                footprints = get_satellite_footprints(soup)
                # Put satellite footprints on queue
                queue_for_footprints.put(footprints)
                break
        except:
            print("Attempt", i + 1, "unsuccessful HTTP request at", url)


def get_satellite_information(soup: BeautifulSoup) -> list:
    """
    Generates a list of information for a given satellite including primary and
    secondary names, position, NORAD ID, and beacon data.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text.

    Returns
    -------
    satellite_information: list
        List of of the following strings: primary satellite name, secondary satellite name, position,
        NORAD ID, and beacons
    """
    satellite_name = find_by_label(soup, "Satellite Name:")
    delimiter = "("
    if delimiter not in satellite_name:
        primary_satellite_name = utilities.standardize_satellite(satellite_name)
        secondary_satellite_name = ""
    else:
        temp = satellite_name.split("(", maxsplit=1)
        primary_satellite_name = utilities.standardize_satellite(temp[0])
        secondary_satellite_name = utilities.standardize_satellite(temp[1])

    position = str(find_by_label(soup, "Position:"))
    norad_id = str(find_by_next(soup, "NORAD:", "a").contents[0])
    beacons = str(find_by_label(soup, "Beacon(s):"))
    satellite_information = [
        primary_satellite_name,
        secondary_satellite_name,
        position,
        norad_id,
        beacons,
    ]
    return satellite_information


def find_by_label(soup: BeautifulSoup, label: str) -> str:
    """
    Find the next node that comes after a specified HTML node.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text
    label: str
        String containing text attribute

    Returns
    -------
    str
        Returns the next node of the specified node
        Returns empty string if next node does not exist

    """
    span = soup.find("b", text=label)
    if span:
        return str(span.next_sibling)
    return ""


def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
    """
    Find the first tag that comes after a given HTML tag.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text
    label: str
        String containing text attribute
    tag: str
        String containing valid html tag

    Returns
    -------
    str
        Returns the first tag that comes after the current tag
    """
    span = soup.select("b", text=label)[0]
    return span.find_next(tag)


def get_satellite_footprints(soup: BeautifulSoup) -> list:
    """
    Generates list of footprint images and image titles.

    Parameters
    ----------
    soup: BeautifulSoup
        BeautifulSoup object containing parsed html text

    Returns
    -------
    [images, image_titles]: list
        List of lists containing footprint image links and corresponding footprint
        image titles.
    """
    # Find all of the appropriate image tags:
    slider_div_element = soup.find("div", {"id": "sliderDiv"})

    # Check is satellite has footprints
    if slider_div_element:
        image_container = slider_div_element.find_all("a")
        if image_container is not None:
            image_titles = []
            image_links = []

            for element in image_container:
                title = element.find("h2").text
                image = element.find("img")

                # Filter for JPG format image links
                if image.attrs["src"].endswith(".jpg"):
                    image_titles.append(title)
                    image_links.append(image.attrs["src"])
                    # image_links = [image for image in image_links]
            tag = "https://satbeams.com"
            images = [tag + i for i in image_links]
            return [images, image_titles]
    return []


def list_to_dict(information: list) -> dict:
    """
    Convert list of lists to dictionary.

    Parameters
    ----------
    information: list
        List of lists containing general satellite information.

    Returns
    -------
    information_dict:
        Dictionary of lists containing general satellite information.
    """
    primary_satellite_names = []
    secondary_satellite_names = []
    satellite_positions = []
    satellite_norads = []
    satellite_beacons = []
    for entry in information:
        primary_satellite_names.append(entry[0])
        secondary_satellite_names.append(entry[1])
        satellite_positions.append(entry[2])
        satellite_norads.append(entry[3])
        satellite_beacons.append(entry[4])

    information_dict = {
        "Primary Satellite Name": primary_satellite_names,
        "Secondary Satellite Name(s)": secondary_satellite_names,
        "Position": satellite_positions,
        "NORAD ID": satellite_norads,
        "Beacons": satellite_beacons,
    }
    return information_dict
