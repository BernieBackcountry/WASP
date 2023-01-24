import pandas as pd
import itertools

import wasp_tool.utilities as utilities


celestrak = pd.read_csv("wasp_tool/data/celestrak.csv", header=0)
lyngsat = pd.read_csv("wasp_tool/data/lyngsat.csv", header=0)
altervista = pd.read_csv("wasp_tool/data/altervista.csv", header=0)
satbeams = pd.read_csv("wasp_tool/data/satbeams.csv", header=0)

path_data = utilities.get_project_path().joinpath('data')

sat_lst = list(itertools.chain(altervista["Satellite"], celestrak["Satellite"], satbeams["Satellite"], lyngsat["Satellite"]))

new_sat = []

for sat_name in sat_lst:
    # strip leading/following spaces
    name_strip = sat_name.strip()
    # cast whole string to upper
    name_upper = name_strip.upper()
    
    # CASE 1: replacing sub-strings for consistency
    case_1 = {"G-SAT": "GSAT", 
        "HELLASSAT": "HELLAS SAT", 
        "HELLAS-SAT": "HELLAS SAT", 
        "HOTBIRD": "HOT BIRD"}
    for substring in case_1.keys():
        if substring in name_upper:
            name_upper = name_upper.replace(substring, case_1[substring])
            break
    
    # CASE 2: replacing white space with dashes
    dash_add = ["ABS", "AMC", "AMOS", "ARABSAT", "ATHENA FIDUS", "BADR", "BSAT", "BEIDOU ", "BULGARIASAT", "CIEL", "CMS", "EXPRESS AT", 
    "EXPRESS AM", "GSAT", "HORIZONS", "INSAT", "JCSAT", "KAZSAT", "MEASAT", "NSS", "PAKSAT", "PSN", "SES", "TKSAT",
    "VIASAT", "VINASAT", "WILDBLUE", "XM "]
    if any(substring in name_upper for substring in dash_add) and ("SERIES" not in name_upper):
        name_upper = name_upper.replace(" ", "-", 1)
    
    # CASE 3: replacing dashes with white space
    dash_remove = ["EXPRESS AMU", "THURAYA"]
    if any(substring in name_upper for substring in dash_remove):
        name_upper = name_upper.replace("-", " ", 1)
    
    new_sat.append(name_upper)
    

master_list = list(set(new_sat))

print(len(master_list))

dict_ = {"Satellite": master_list}

utilities.save_dict_to_csv(path_data, dict_, "master-fixed.csv")



# same satellites
# ALPHASAT ALPHASAT I-XL
# ASIASTAR ASIASTAR 1
# Astra 2E Astra 2E (Eutelsat 28E)
# Astra 2F Astra 2F (Eutelsat 28F)
# Astra 2G Astra 2G (Eutelsat 28G)
# AZERSPACE AZERSPACE 1
# Azerspace 2 Azerspace 2/Intelsat 38
# Bangabandhu 1 Bangabandhusat 1
# Belintersat 1 Belintersat 1 (Chinasat 15)
# Bsat 3C Bsat 3C/Jcsat 110R
# Express Am6 Express Am6 (Eutelsat 53A)
# Express Amu1 Express Amu1 (Eutelsat 36C)
# Galaxy 13 Galaxy 13 Horizons 1 Galaxy 13/Horizons 1
# Hispasat 143W 1 Hispasat 1D
# Hispasat 1E Hispasat 30W 5
# Hispasat 1F Hispasat 30W 6
# TurkmenÃ¤lem/Monacosat Turkmenalem Turkmenalem52E/Monacosat
# Telstar 18 Vantage (Apstar 5C) Telstar 18V
# Telstar 12 Vantage Telstar 12V
# Sgdc Sgdc 1
# Rascom 1R Rascom Qaf 1R
# Quetzsat Quetzsat 1
# PSN-6 Nusantara Satu
# Mexsat 3 Mexsat Bicentenario




# CO-OWNED
# ASIASAT6/THAICOM 6
# Echostar 105/Ses 11
# Echostar 9/Galaxy 23


# SERIES
# ARABSAT 1 Series : 


# Even a satellite?
# Express
# Hellas Sat 4 & Sgs 1
# Hispasat 74W 1		is an amazonas
# Hns 95W		is an echostar
# Ico G1		is an echostar

# T10/T12		same channels I guess on Lyngsat
# T11/T14		

# Sbs 1 To 4
