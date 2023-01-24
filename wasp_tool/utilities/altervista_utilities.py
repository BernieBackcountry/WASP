import requests
from bs4 import BeautifulSoup

import wasp_tool.utilities as utilities


def prepare_altervista(url: str):
    sat_urls = get_urls(url)
    pri_satNames = []
    pdf_urls = []
    for sat in sat_urls:
        sat_list, url_list = get_pdf_urls(sat)
        pri_satNames.extend(sat_list)
        pdf_urls.extend(url_list)
    return pri_satNames, pdf_urls


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
    urls = []
    sats = []
    for a in sidebar.find_all('a', href=True):
        if ".pdf" in a['href']:
            urls.append(a['href'])
            # TODOOOOOOOOOOOOOOOOOOOOOOOOOO need to add fucntionality to clean this up
            temp = a.text
            pri_satName = utilities.standardize_satellite(temp)
            sats.append(pri_satName)
    return sats, urls


def get_pdf_name(pdf: str):  
    ele = pdf.split("/")[-1]
    ele = ele.replace(".pdf", "")
    pdf_name = ele.replace("_", " ")
    return pdf_name
