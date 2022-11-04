import queue
from bs4 import BeautifulSoup
import re
import requests
import threading
import pickle
from tqdm import tqdm
from pathlib import Path


# CelesTrak Functions
def prepare_text(text: list) -> dict:
    tle_dict = {}
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")
            tle_dict[line.strip()] = tle_1 + "\n" + tle_2
    return tle_dict


def save_text(path: Path, dict_: dict):
    with open(path / 'celestrak.pkl', 'wb') as f:
        pickle.dump(dict_, f)


# Satbeam Functions
def get_all_urls(soup: BeautifulSoup, headers: dict) -> list:
    urls = []
    for link in soup.findAll('a', {'class': 'link'}):
        urls.append("https://satbeams.com"+str((link['href'])))
    return urls


def run_threads(soup: BeautifulSoup, headers: dict, path: Path):
    thread_results = []
    q = queue.Queue()
    all_urls = get_all_urls(soup, headers)
    all_urls = all_urls
    threads = [threading.Thread(target=fetch_url, args=(url, headers, path, q)) for url in all_urls]
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)
    for thread in threads:
        thread.join()
    return thread_results


def fetch_url(url, headers, path, q):
    response = requests.get(url, headers=headers)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        # Scrap satellite info
        sat_id, pos, norad = get_satellite_info(soup)
        # Put satellite info on queue
        q.put([sat_id, pos, norad])
        # Scrap images info
        images = get_satellite_footprints(soup)
        # Save images 
        save_satellite_footprints(sat_id, path, images)


def find_by_label(soup: BeautifulSoup, label: str) -> str:
    return str(soup.find("b", text=re.compile(label)).next_sibling)


def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
    span = soup.select("b", text=re.compile(label))[0]
    return span.find_next(tag)


def get_satellite_info(soup: BeautifulSoup) -> str:
    sat = find_by_label(soup, "Satellite Name:")
    if "(" in sat:
        temp = sat.split("(", 1)[0]
        sat_id = temp.upper().strip()
    else:
        sat_id = sat.upper().strip()
    position = str(find_by_label(soup, "Position:"))
    norad = str(find_by_next(soup, "NORAD:", "a").contents[0])
    return sat_id, position, norad


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
    # download and save images 
    for image in tqdm(images):
        file_name = image.split('/')[-1]
        file_name = sat_id + "-" + file_name
        try:
            r = requests.get(image, stream=True)
            if r.status_code == 200:
                with open(path / file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        except Exception as e:
            pass    


def list_to_dict(output) -> dict:
    dict_ = {}
    for ele in output:
        for e in ele:
            dict_[e[0]] = e[1] + e[2]
    return dict_


def save_satellite_info(output, path: Path):
    dict_ = list_to_dict(output)
    with open(path / 'satbeam.pkl', 'wb') as f:
        pickle.dump(dict_, f)
