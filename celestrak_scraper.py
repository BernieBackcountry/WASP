import urllib.request
import pandas as pd

import utilities


path = utilities.get_project_path().joinpath('data')
urllib.request.urlretrieve("https://celestrak.com/NORAD/elements/geo.txt", path / "celestrak_geo.txt")

read_file = pd.read_csv(path.joinpath("celestrak_geo.txt"))
read_file.to_csv(path / "celestrak_geo.csv", index=None)
