import pandas as pd

import wasp_tool.utilities as utilities

path = utilities.get_project_path().joinpath("wasp_tool", "assets", "geostationary_satellites.csv")
df = pd.read_csv(path, header=0)
print(df)