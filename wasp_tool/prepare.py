import requests
from bs4 import BeautifulSoup

import wasp_tool.utilities as utilities


# create data directory
utilities.create_directory(utilities.get_project_path().joinpath('data'))

path1 = utilities.get_project_path().joinpath('data')
path2 = utilities.get_project_path().joinpath('data', 'images')

# Scrap Celestrak data
celestrak_data = utilities.prepare_tles("https://celestrak.com/NORAD/elements/geo.txt")
utilities.save_dict_as_csv(path1, celestrak_data, "celestrak.csv")


# Scrap Satbeam data
#satbeam_text = requests.get('https://satbeams.com/satellites?status=active').text
#soup = BeautifulSoup(satbeam_text, "html.parser")
#utilities.run_threads(soup, {"User-Agent": "Chrome/51.0.2704.103",}, path1, path2)


# Scrap Lyngsat data
#lyngsat_tables = utilities.get_lyngsat_tables('https://www.lyngsat.com/')
#utilities.save_tables(path1, lyngsat_tables)
