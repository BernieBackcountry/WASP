import wasp_tool.utilities as utilities


path = utilities.get_project_path().joinpath('wasp_tool')
print(path)

# create data directory
path_data = path.joinpath('data')
utilities.create_directory(path_data)


# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")
print("CELESTRAK COMPLETE")
