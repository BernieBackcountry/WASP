import requests

import wasp_tool.utilities as utilities


def prepare_celestrak(url: str) -> dict:
    tle_dict = {}
    text = get_tles(url) # get TLE data
    pri_sat, sec_sat, tle_data = prepare_tles(text) # prepare TLE data
    tle_dict = {'priSatName': pri_sat, 
                'secSatName': sec_sat,
                'TLE': tle_data}              
    return tle_dict


def get_tles(url: str) -> list:
    response = requests.get(url) # Heroku has specified timeout
    if response.status_code == 200:
        text = response.text.split("\n")
        return text
    else:
        print("Unsuccessful request at ", url)


def prepare_tles(text: list) -> list:
    pri_name, sec_name, tles = ([] for i in range(3))
    # iterate through lines to get sat names and corresponding TLEs
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")  
            tles.append(tle_1 + "\n" + tle_2)
            # separate out pri and sec sat names
            if "(" not in line:
                pri_name.append(utilities.standardize_satellite(line))
                sec_name.append("")      
            else:
                temp = line.split("(")
                pri_name.append(utilities.standardize_satellite(temp[0]))
                sec_name.append(utilities.standardize_satellite(temp[1]))              
    return pri_name, sec_name, tles
    