import requests

import utilities as utilities


def prepare_text(text: list) -> dict:
    dict_ = {}
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")
            dict_[line.strip()] = tle_1 + "\n" + tle_2
    return dict_


path = utilities.get_project_path().joinpath('data')
text = requests.get("https://celestrak.com/NORAD/elements/geo.txt").text.split("\n")

output = prepare_text(text)
print(output)
