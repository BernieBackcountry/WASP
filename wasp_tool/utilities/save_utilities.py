import pandas as pd
from pathlib import Path
import threading
from tqdm import tqdm
import requests

import wasp_tool.utilities as utilities

def save_dict_to_csv(path: Path, dict_: dict, file_name: str):
    df = pd.DataFrame(dict_)
    df.to_csv(path / file_name, index=False)


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
