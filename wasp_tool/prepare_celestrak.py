import wasp_tool.utilities as utilities


# create data directory and sub-directories
path = utilities.get_project_path().joinpath('data')

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")
print("CELESTRAK COMPLETE")
