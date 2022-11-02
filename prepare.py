import requests
from bs4 import BeautifulSoup
import pickle

import utilities as utilities
from utilities.prepare_utilities import save_satellite_info

path1 = utilities.get_project_path().joinpath('data')
path2 = utilities.get_project_path().joinpath('data', 'images')

# Scrap Celestrak data
celestrak_text = requests.get("https://celestrak.com/NORAD/elements/geo.txt").text.split("\n")

celestrak_info = utilities.prepare_text(celestrak_text)
utilities.save_text(path1, celestrak_info)

# with open(path / 'celestrak.pkl', 'rb') as f:
#     loaded_dict = pickle.load(f)

# print(loaded_dict)

satbeam_text = requests.get('https://satbeams.com/satellites?status=active').text
soup = BeautifulSoup(satbeam_text, "html.parser")
res = utilities.run_threads(soup, {"User-Agent": "Chrome/51.0.2704.103",}, path2)

print("DONE")

save_satellite_info(res, path1)

with open(path1 / 'satbeam.pkl', 'rb') as f:
    loaded_dict = pickle.load(f)

print(loaded_dict)
