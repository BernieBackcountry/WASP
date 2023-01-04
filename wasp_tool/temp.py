from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import itertools
import re

import wasp_tool.utilities as utilities


def get_region_urls(link):
    text = requests.get(link).text
    soup = BeautifulSoup(text, 'lxml')
    asia = link + str(soup.find('a', text='Asia', href=True)['href'])
    europe = link + str(soup.find('a', text='Europe', href=True)['href'])
    atlantic = link + str(soup.find('a', text='Atlantic', href=True)['href'])
    america = link + str(soup.find('a', text='America', href=True)['href'])
    print([asia, europe, atlantic, america])
    return [asia, europe, atlantic, america]


def get_satellite_urls(url):
    response = requests.get(url, timeout=20)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'lxml')
        # create dictionary with href as value and satName as key
        href_all = {}
        for href in soup.find_all('a', href=True):
            href_all[href.text] = href['href']
        # remove extraneous href entries 
        href_sub = dict([(k,val) for k,val in href_all.items() if "http" not in val and "and" not in val])
        # remove repeat entries with incorrect key values 
        href_final = dict([(k,val) for k,val in href_sub.items() if "." not in k])
        # create sat list 
        sat_list = list(href_final.keys())
        # convert hrefs to urls and create url list
        url_list = ["https://www.lyngsat.com/" + s for s in href_final.values()]
        return sat_list, url_list


def get_lyngsat_info(main_page):
    # obtain satellite regions
    region_urls = get_region_urls(main_page)

    satNames = []
    satUrls = []
    # obtain sat names and corresponding urls for all regions
    for region in region_urls:
        sat_list, url_list = get_satellite_urls(region)
        satNames.extend(sat_list)
        satUrls.extend(url_list)

    # scrap each sat page for table information


main_page = 'https://www.lyngsat.com/'
get_lyngsat_info(main_page)

# think we want to keep the dictionary aspect to make table keeping easy 
# df columns are [Satellite Name, Frequency Polarity, Transponder, Beam, EIRP(dBW), System, SR, FEC, Provider Name, Channel Name]

