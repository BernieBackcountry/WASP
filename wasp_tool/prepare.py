import requests
from bs4 import BeautifulSoup

import wasp_tool.utilities as utilities


# create data directory
utilities.create_directory(utilities.get_project_path().joinpath('data'))

path_data = utilities.get_project_path().joinpath('data')
path_images = utilities.get_project_path().joinpath('data', 'images')

# Scrap Celestrak data
#celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
#utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")


# Scrap Satbeams data
satbeams_data, satbeams_footprints = utilities.prepare_satbeams('https://satbeams.com/satellites?status=active')
utilities.save_dict_to_csv(path_data, satbeams_data, "satbeams.csv")
utilities.save_footprints(satbeams_footprints)

#satbeam_text = requests.get('https://satbeams.com/satellites?status=active').text
#soup = BeautifulSoup(satbeam_text, "html.parser")
#utilities.run_threads(soup, {"User-Agent": "Chrome/51.0.2704.103",}, path1, path2)


# Scrap Lyngsat data
#lyngsat_data = utilities.prepare_tables('https://www.lyngsat.com/')

#lyngsat_tables = utilities.get_lyngsat_tables('https://www.lyngsat.com/')
#utilities.save_dict_to_csv(path_data, lyngsat_data, "lyngsat.csv")
