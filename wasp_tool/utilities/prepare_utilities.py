import pandas as pd
from pathlib import Path
import threading
from tqdm import tqdm
import requests
from pdf2image import convert_from_path
import os

import wasp_tool.utilities as utilities


def standardize_satellite(sat_name: str) -> str:
    # strip end parenthesis 
    name_replace = sat_name.replace(")", "")
    # strip leading/following spaces
    name_strip = name_replace.strip()
    # cast whole string to upper
    name_upper = name_strip.upper()
    
    # CASE 1: replacing sub-strings for consistency
    case_1 = {"G-SAT": "GSAT", 
        "HELLASSAT": "HELLAS SAT", 
        "HELLAS-SAT": "HELLAS SAT", 
        "HOTBIRD": "HOT BIRD"}
    for substring in case_1.keys():
        if substring in name_upper:
            name_upper = name_upper.replace(substring, case_1[substring])
            break
    
    # CASE 2: replacing white space with dashes
    dash_add = ["ABS", "AMC", "AMOS", "ARABSAT", "ATHENA FIDUS", "BADR", "BSAT", "BEIDOU ", 
        "BULGARIASAT", "CIEL", "CMS", "EXPRESS AT", "EXPRESS AM", "GSAT", "HORIZONS", "INSAT", 
        "JCSAT", "KAZSAT", "MEASAT", "NSS", "PAKSAT", "PSN", "SES", "TKSAT", "VIASAT", "VINASAT", 
        "WILDBLUE", "XM "]
    if (any(substring in name_upper for substring in dash_add)) and ("SERIES" not in name_upper):
        name_upper = name_upper.replace(" ", "-", 1)
    
    # CASE 3: replacing dashes with white space
    dash_remove = ["EXPRESS AMU", "THURAYA"]
    if any(substring in name_upper for substring in dash_remove):
        name_upper = name_upper.replace("-", " ", 1)

    new_name = name_upper
    return new_name


def save_dict_to_csv(path: Path, dict_: dict, file_name: str):
    df = pd.DataFrame(dict_)
    df.to_csv(path.joinpath(file_name), index=False)


def save_footprints(path: Path, sat_names: list, footprints: list):
    images, titles = map(list, zip(*footprints))
    threads = [threading.Thread(target=image_download, args=(path, sat, images, titles, k)) for k, sat in enumerate(sat_names)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    
def image_download(path: Path, sat_name: str, image_links: list, image_titles: list, iter: int):
    utilities.create_directory(path.joinpath(sat_name))
    path = path.joinpath(sat_name)
    sat_images = image_links[iter]
    sat_titles = image_titles[iter]
    # download and save images 
    for i, image in tqdm(enumerate(sat_images)):
        file_name = sat_titles[i] + ".jpg"
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                with open(path / file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        except Exception as e:
            pass 


def save_tables(path: Path, dict_: dict):
    for key, lst in dict_.items():
        # / causes problem with directory name
        if "/" in key:
            key = key.replace("/", "-")
        utilities.create_directory(path.joinpath(key))
        file_path = path.joinpath(key)
        for i, ele in enumerate(lst): 
            file_name = key + "_" + str(i) + ".csv"
            ele.to_csv(file_path / file_name, index=False)


def save_pdfs(path: Path, names: list, urls: list):
    for i, url in enumerate(urls):
        sat_name = names[i]
        utilities.create_directory(path.joinpath(sat_name))
        file_path = path.joinpath(sat_name)
        try:
            req = requests.get(url, timeout=20)
            pdf_name = sat_name + ".pdf"
            print("File", sat_name, "downloading")
            # write to pdf
            pdf = open(file_path / pdf_name, 'wb')
            pdf.write(req.content)
            pdf.close()
            # save pdf as new jpg
            pages = convert_from_path(file_path / pdf_name)
            for i, page in enumerate(pages):
                jpg_name = sat_name + "_" + str(i) + ".jpg"
                page.save(file_path / jpg_name, 'JPEG', optimize=True, quality=75)
            # delete original pdf
            os.remove(file_path / pdf_name)
        except:
            print("Unable to download", sat_name)
            pass
