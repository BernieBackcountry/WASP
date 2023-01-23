import requests

import wasp_tool.utilities as utilities


def prepare_celestrak(url: str) -> dict:
    tle_dict = {}
    pri_satName, sec_satName, tle = ([] for i in range(3))
    # get TLE data
    text = get_tles(url)
    
    # iterate through lines to get sat name and corresponding TLEs
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")  
            # separate out pri and sec sat names
            if "(" not in line:
                pri_satName.append(utilities.standardize_satellite(line))
                sec_satName.append("")      
            else:
                temp = line.split("(")
                pri_satName.append(utilities.standardize_satellite(temp[0]))
                sec_satName.append(utilities.standardize_satellite(temp[1]))
                
            tle.append(tle_1 + "\n" + tle_2)
    
    tle_dict = {'priSatName': pri_satName, 
                'secSatName': sec_satName,
                'TLE': tle}
                
    return tle_dict


def get_tles(url: str) -> list:
    return requests.get(url).text.split("\n")
