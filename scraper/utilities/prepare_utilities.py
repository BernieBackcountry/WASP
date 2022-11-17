import queue
import pandas as pd
from bs4 import BeautifulSoup
import re
import requests
import threading
import pickle
from tqdm import tqdm
from pathlib import Path

import scraper.utilities as utilities 

# CelesTrak Functions
def prepare_text(text: list) -> dict:
    tle_dict = {}
    sat = []
    sat_extra = []
    tle = []
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")
            sat_temp = line.strip().replace("-", " ")
            if "(" in sat_temp:
                temp = sat_temp.split("(", 1)
                sat_id = temp[0].upper().strip()
                sat.append(sat_id)
                temp_2 = temp[1]
                sat_extra.append(temp_2[:-1])
            else:
                sat_extra.append("")
                sat.append(sat_temp)
            tle.append(tle_1 + "\n" + tle_2)
    tle_dict = {'Satellite': sat, 
                'Extra': sat_extra,
                'Telemetry': tle}
    return tle_dict


def save_text(path: Path, dict_: dict):
    df = pd.DataFrame(dict_)
    df.to_csv(path / 'celestrak.csv', index=False)


# Satbeam Functions
def get_all_urls(soup: BeautifulSoup, headers: dict) -> list:
    urls = []
    for link in soup.findAll('a', {'class': 'link'}):
        urls.append("https://satbeams.com"+str((link['href'])))
    return urls


def run_threads(soup: BeautifulSoup, headers: dict, path1: Path, path2: Path):
    thread_results = []
    q = queue.Queue()
    all_urls = get_all_urls(soup, headers)
    all_urls = all_urls[:15]
    threads = [threading.Thread(target=fetch_url, args=(url, headers, path2, q)) for url in all_urls]
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)
    for thread in threads:
        thread.join()
    save_satellite_info(thread_results, path1)
    

def fetch_url(url, headers, path, q):
    response = requests.get(url, headers=headers, timeout=20)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        # Scrap satellite info
        sat_id, sat_extra, pos, norad, beacon = get_satellite_info(soup)
        # Put satellite info on queue
        q.put([sat_id, sat_extra, pos, norad, beacon])
        # Create image directories
        create_image_directories(sat_id, path)
        # Scrap images info
        images = get_satellite_footprints(soup)
        # Save images 
        save_satellite_footprints(sat_id, path, images)


def find_by_label(soup: BeautifulSoup, label: str) -> str:
    span = soup.find("b", text=label)
    if span:
        return str(span.next_sibling)
    else:
        return ""


def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
    span = soup.select("b", text=label)[0]
    return span.find_next(tag)


def get_satellite_info(soup: BeautifulSoup) -> str:
    sat = find_by_label(soup, "Satellite Name:")
    sat = sat.replace("-", " ")
    if "(" in sat:
        temp = sat.split("(", 1)
        sat_id = temp[0].upper().strip()
        temp_2 = temp[1]
        sat_extra = temp_2[:-1]
    else:
        sat_id = sat.upper().strip()
        sat_extra = ""
    position = str(find_by_label(soup, "Position:"))
    norad = str(find_by_next(soup, "NORAD:", "a").contents[0])
    beacon = str(find_by_label(soup, "Beacon(s):"))
    return sat_id, sat_extra, position, norad, beacon
    

def create_image_directories(satellite: str, path: Path):
    utilities.create_directory(path.joinpath(satellite))


def get_satellite_footprints(soup: BeautifulSoup) -> list:
    # Find all of the image tags:
    images = soup.findAll('img')
    # Extract 'src' attribute of every image
    image_links = []
    for image in images:
        image_links.append(image.attrs['src'])
        #Filter for JPG format image links
        image_links = [image for image in image_links if image.endswith('.jpg')]      
    one = 'https://satbeams.com'
    images =  [one+i for i in image_links]
    return images 


def save_satellite_footprints(sat_id: str, path: Path, images: list):
    path = path.joinpath(sat_id)
    # download and save images 
    for image in tqdm(images):
        file_name = image.split('/')[-1]
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                with open(path / file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        except Exception as e:
            pass    


def save_satellite_info(results: list, path: Path):
    sat = []
    sat_extra = []
    pos = []
    nor = []
    beac = []
    for ele in results:
        sat.append(ele[0])
        sat_extra.append(ele[1])
        pos.append(ele[2])
        nor.append(ele[3])
        beac.append(ele[4])
    dict_ = {'Satellite': sat,
            'Extra': sat_extra,
            'Position': pos,
            'NORAD': nor, 
            'Beacon': beac}
    df = pd.DataFrame(dict_)
    df.to_csv(path / 'satbeam.csv', index=False)