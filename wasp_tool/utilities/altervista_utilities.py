import requests
from bs4 import BeautifulSoup


def prepare_altervista(url: str):
    sat_urls = get_urls(url)
    sat_names = []
    pdf_urls = []
    for sat in sat_urls:
        temp_pdf, temp_sat = get_pdf_urls(sat)
        sat_names.extend(temp_sat)
        pdf_urls.extend(temp_pdf)
    return sat_names, pdf_urls


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
            sats.append(get_pdf_name(a['href']))
    return urls, sats


def get_pdf_name(pdf: str):  
    ele = pdf.split("/")[-1]
    ele = ele.replace(".pdf", "")
    ele = ele.replace("_", " ")
    pdf_name = ele.strip()
    return pdf_name
