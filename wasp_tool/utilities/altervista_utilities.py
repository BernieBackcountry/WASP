import requests
from bs4 import BeautifulSoup


def prepare_altervista(url: str):
    sat_urls = get_urls(url, False)
    pdf_urls = []
    for sat in sat_urls:
        pdf_urls.extend(get_urls(sat, True))
    return pdf_urls


def get_urls(url: str, pdf: bool) -> list:
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    sidebar = soup.find("div", id="sidebar")
    urls = []
    for a in sidebar.find_all('a', href=True):
        if pdf:
            if ".pdf" in a['href']:
                urls.append(a['href'])
        else:
            urls.append(a['href'])
    return urls
