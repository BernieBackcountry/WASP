import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

import wasp_tool.utilities as utilities


def save_dict_to_csv(path: Path, dict_: dict, file_name: str):
    df = pd.DataFrame(dict_)
    df.to_csv(path / file_name, index=False)


def save_footprints(footprints: list):
    images, titles = map(list, zip(*footprints))
    #path = path.joinpath(sat_id)
    # download and save images 
    for i, image in tdqm(enumerate(images)):
        file_name = titles[i] + ".jpg"
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                with open(path / file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        except Exception as e:
            pass    
            
