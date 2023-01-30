import requests
from bs4 import BeautifulSoup

import wasp_tool.utilities as utilities


def prepare_altervista(url: str):
    sat_urls = get_urls(url)
    sat_dict = {}
    pri_satNames, sec_satNames, pdf_urls = ([] for i in range(3))
    for sat in sat_urls:
        pri_sat, sec_sat, url_list = get_pdf_urls(sat)
        pri_satNames.extend(pri_sat)
        sec_satNames.extend(sec_sat)
        pdf_urls.extend(url_list)

    sat_dict = {"priSatName": pri_satNames,
                "secSatName": sec_satNames}
    return sat_dict, pdf_urls


def get_urls(url: str) -> list:
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    sidebar = soup.find("div", id="sidebar")
    urls = []
    for a in sidebar.find_all('a', href=True):
        urls.append(a['href'])
    return urls


def get_pdf_urls(url: str) -> list:
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    sidebar = soup.find("div", id="sidebar")
    priSats, secSats, urls = ([] for i in range(3)) 
    for a in sidebar.find_all('a', href=True):
        if ".pdf" in a['href']:
            urls.append(a['href'])
            temp = a.text
            pri_sat, sec_sat = get_sats(temp)
            pri_satName = utilities.standardize_satellite(pri_sat)
            sec_satName = utilities.standardize_satellite(sec_sat)
            priSats.append(pri_satName)
            secSats.append(sec_satName)
    return priSats, secSats, urls


def get_sats(text: str):
    delimiters = ["(", "-->", "-- >", "--"]
    if any(s in text for s in delimiters):
        min = 1000
        for delim in delimiters:
            if (text.find(delim) != -1) and (text.find(delim) < min):
                min = text.find(delim)
                split_by = delim
        priSatName, secSatName = split_text(text, split_by)
    else:
        priSatName = text
        secSatName = ""
    return priSatName, secSatName


def split_text(text: str, split_on: str):
    text_split = text.split(split_on, 1)
    pri = text_split[0]
    sec = text_split[1]
    return pri, sec