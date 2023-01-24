import wasp_tool.utilities as utilities


# create data directory and sub-directories
# utilities.create_directory(utilities.get_project_path().joinpath('data', 'images'))
# utilities.create_directory(utilities.get_project_path().joinpath('data', 'pdfs'))
# utilities.create_directory(utilities.get_project_path().joinpath('data', 'tables'))

path_data = utilities.get_project_path().joinpath('data')
path_images = utilities.get_project_path().joinpath('data', 'images')
path_pdfs = utilities.get_project_path().joinpath('data', 'pdfs')
path_tables = utilities.get_project_path().joinpath('data', 'tables')

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")
print("Celestrak DONE")

# Scrap Satbeams data
# satbeams_data, satbeams_footprints = utilities.prepare_satbeams('https://satbeams.com/satellites?status=active')
# utilities.save_dict_to_csv(path_data, satbeams_data, "satbeams.csv")
# # # print(satbeams_footprints)
# # # utilities.save_footprints(path_images, satbeams_data["Satellite"], satbeams_footprints)
# print("Satbeams DONE")

# Scrap Lyngsat data
lyngsat_data = utilities.prepare_lyngsat('https://www.lyngsat.com/')
utilities.save_dict_to_csv(path_data, {"priSatName": list(lyngsat_data.keys())}, "lyngsat.csv")
# utilities.save_tables(path_tables, lyngsat_data)
# lyngsat has () and then / to deal with 
print("Lyngsat DONE")

# # Scrap Altervista data
# altervista_data, altervista_pdfs = utilities.prepare_altervista('http://frequencyplansatellites.altervista.org/')
# utilities.save_dict_to_csv(path_data, {"priSatName": altervista_data}, "altervista.csv")
# #utilities.save_pdfs(path_pdfs, altervista_data, altervista_pdfs)
# print("Altervista DONE") 