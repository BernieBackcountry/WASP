import requests
from bs4 import BeautifulSoup

import wasp_tool.utilities as utilities

path1 = utilities.get_project_path().joinpath('data')
path2 = utilities.get_project_path().joinpath('data', 'images')

# Scrap Celestrak data
celestrak_text = requests.get("https://celestrak.com/NORAD/elements/geo.txt").text.split("\n")

celestrak_info = utilities.prepare_text(celestrak_text)
utilities.save_text(path1, celestrak_info)


# # Scrap Satbeam data
satbeam_text = requests.get('https://satbeams.com/satellites?status=active').text
soup = BeautifulSoup(satbeam_text, "html.parser")
utilities.run_threads(soup, {"User-Agent": "Chrome/51.0.2704.103",}, path1, path2)
