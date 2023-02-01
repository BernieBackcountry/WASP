import wasp_tool.utilities as utilities


path = utilities.get_project_path().resolve().parent.joinpath('wasp_tool')

# create data directory
utilities.create_directory(path.joinpath('data'))
path_data = path.joinpath('data')

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")
print("CELESTRAK COMPLETE")
