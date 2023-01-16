import requests


def prepare_celestrak(url: str) -> dict:
    tle_dict = {}
    sat_name, sat_name_excess, tle = ([] for i in range(3))
    
    # get TLE data
    text = get_tles(url)
    
    # iterate through lines to get sat name and corresponding TLEs
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")
            sat = line.strip().replace("-", " ")
            # strip excess sat names
            if "(" in sat:
                temp = sat.split("(", 1)
                sat_id = temp[0].upper().strip()
                sat_name.append(sat_id)
                temp_2 = temp[1]
                sat_name_excess.append(temp_2[:-1])
            else:
                sat_name.append(sat)
                sat_name_excess.append("")
                
            tle.append(tle_1 + "\n" + tle_2)
    
    tle_dict = {'Satellite': sat_name, 
                'Extra Names': sat_name_excess,
                'TLE': tle}
                
    return tle_dict


def get_tles(url: str) -> list:
    return requests.get(url).text.split("\n")
