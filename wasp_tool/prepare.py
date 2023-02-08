import wasp_tool.utilities as utilities
import time

# create data directory and sub-directories
path = utilities.get_project_path().joinpath('wasp_tool')
path_data = path.joinpath('data')
path_footprints = path.joinpath('data', 'footprints')
path_freq_plans = path.joinpath('data', 'freq_plans')
path_channels = path.joinpath('data', 'channels')

start_time = time.time()

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(path_data, celestrak_data, "celestrak.csv")
print("--- %s seconds ---" % (time.time() - start_time))
print("CELESTRAK COMPLETE")

# Scrap Altervista data
altervista_data, altervista_pdfs = utilities.prepare_altervista('http://frequencyplansatellites.altervista.org/')
utilities.save_dict_to_csv(path_data, altervista_data, "altervista.csv")
utilities.save_pdfs(path_freq_plans, altervista_data['priSatName'], altervista_pdfs)
print("--- %s seconds ---" % (time.time() - start_time))
print("ALTERVISTA COMPLETE") 

# Scrap Satbeams data
satbeams_data, satbeams_footprints = utilities.prepare_satbeams('https://satbeams.com/satellites?status=active')
utilities.save_dict_to_csv(path_data, satbeams_data, "satbeams.csv")
utilities.save_footprints(path_footprints, satbeams_data["priSatName"], satbeams_footprints)
print("--- %s seconds ---" % (time.time() - start_time))
print("SATBEAMS COMPLETE")

# Scrap Lyngsat data
lyngsat_data, lyngsat_tables = utilities.prepare_lyngsat('https://www.lyngsat.com/')
utilities.save_dict_to_csv(path_data, lyngsat_data, "lyngsat.csv")
utilities.save_tables(path_channels, lyngsat_tables)
print("--- %s seconds ---" % (time.time() - start_time))
print("LYNGSAT COMPLETE")
