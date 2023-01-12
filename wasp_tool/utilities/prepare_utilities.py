import queue
import pandas as pd
from bs4 import BeautifulSoup
import requests
import threading
from tqdm import tqdm
from pathlib import Path
import numpy as np
import re

import wasp_tool.utilities as utilities 

# CelesTrak Functions
def prepare_text(text: list) -> dict:
    tle_dict = {}
    sat = []
    sat_extra = []
    tle = []
    for i, line in enumerate(text):
        if (i % 3 == 0) and (i <= len(text)-3):
            tle_1 = text[i+1].strip().replace(" ", "*")
            tle_2 = text[i+2].strip().replace(" ", "*")
            sat_temp = line.strip().replace("-", " ")
            if "(" in sat_temp:
                temp = sat_temp.split("(", 1)
                sat_id = temp[0].upper().strip()
                sat.append(sat_id)
                temp_2 = temp[1]
                sat_extra.append(temp_2[:-1])
            else:
                sat_extra.append("")
                sat.append(sat_temp)
            tle.append(tle_1 + "\n" + tle_2)
    tle_dict = {'Satellite': sat, 
                'Extra': sat_extra,
                'Telemetry': tle}
    return tle_dict


def save_text(path: Path, dict_: dict):
    df = pd.DataFrame(dict_)
    df.to_csv(path / 'celestrak.csv', index=False)


# Satbeam Functions
def get_all_urls(soup: BeautifulSoup, headers: dict) -> list:
    urls = []
    for link in soup.findAll('a', {'class': 'link'}):
        urls.append("https://satbeams.com"+str((link['href'])))
    return urls


def run_threads(soup: BeautifulSoup, headers: dict, path1: Path, path2: Path):
    thread_results = []
    q = queue.Queue()
    all_urls = get_all_urls(soup, headers)
    all_urls = all_urls
    threads = [threading.Thread(target=fetch_url, args=(url, headers, path2, q)) for url in all_urls]
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)
    for thread in threads:
        thread.join()
    save_satellite_info(thread_results, path1)
    

def fetch_url(url, headers, path, q):
    response = requests.get(url, headers=headers, timeout=20)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        # Scrap satellite info
        sat_id, sat_extra, pos, norad, beacon = get_satellite_info(soup)
        # Put satellite info on queue
        q.put([sat_id, sat_extra, pos, norad, beacon])
        # Create image directories
        create_image_directories(sat_id, path)
        # Scrap images info
        images, image_titles = get_satellite_footprints(soup)
        # Save images 
        save_satellite_footprints(sat_id, path, images, image_titles)


def find_by_label(soup: BeautifulSoup, label: str) -> str:
    span = soup.find("b", text=label)
    if span:
        return str(span.next_sibling)
    else:
        return ""


def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
    span = soup.select("b", text=label)[0]
    return span.find_next(tag)


def get_satellite_info(soup: BeautifulSoup) -> str:
    sat = find_by_label(soup, "Satellite Name:")
    sat = sat.replace("-", " ")
    if "(" in sat:
        temp = sat.split("(", 1)
        sat_id = temp[0].upper().strip()
        temp_2 = temp[1]
        sat_extra = temp_2[:-1]
    else:
        sat_id = sat.upper().strip()
        sat_extra = ""
    position = str(find_by_label(soup, "Position:"))
    norad = str(find_by_next(soup, "NORAD:", "a").contents[0])
    beacon = str(find_by_label(soup, "Beacon(s):"))
    return sat_id, sat_extra, position, norad, beacon
    

def create_image_directories(satellite: str, path: Path):
    utilities.create_directory(path.joinpath(satellite))


def get_satellite_footprints(soup: BeautifulSoup) -> list:
    # Find all of the appropriate image tags:
    temp = soup.find('div', {'id': 'sliderDiv'})
    images = temp.find_all('img')
    # Extract 'src' attribute of every image
    image_links = []
    image_titles = []
    for image in images:
        #Filter for JPG format image links
        if image.attrs['src'].endswith('.jpg'):
            image_links.append(image.attrs['src'])
            #Find corresponding image titles
            image_titles.append(image.find_previous_sibling('h2').text)
            image_links = [image for image in image_links]      
    one = 'https://satbeams.com'
    images =  [one+i for i in image_links]
    return images, image_titles


def save_satellite_footprints(sat_id: str, path: Path, images: list, image_titles: list):
    path = path.joinpath(sat_id)
    # download and save images 
    for i, image in tqdm(enumerate(images)):
        file_name = image_titles[i] + ".jpg"
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                with open(path / file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        except Exception as e:
            pass    


def save_satellite_info(results: list, path: Path):
    sat = []
    sat_extra = []
    pos = []
    nor = []
    beac = []
    for ele in results:
        sat.append(ele[0])
        sat_extra.append(ele[1])
        pos.append(ele[2])
        nor.append(ele[3])
        beac.append(ele[4])
    dict_ = {'Satellite': sat,
            'Extra': sat_extra,
            'Position': pos,
            'NORAD': nor, 
            'Beacon': beac}
    df = pd.DataFrame(dict_)
    df.to_csv(path / 'satbeam.csv', index=False)


#Lyngsat Functions
def get_lyngsat_tables(main_page: str) -> dict:
    region_urls = get_region_urls(main_page)
    lyngsat_dict = {}
    for region in region_urls:
        # dict sat names and href for each region
        sat_dict = get_satellite_urls(region)
        # loop through each regional satellite
        for key, val in sat_dict.items():
            sat_name = key
            # send in url 
            key_tables = get_key_tables(val)
            # check for empty pages
            if not key_tables:
                continue
            else:
                tables_clean = read_tables(sat_name, key_tables)
                lyngsat_dict[sat_name] = tables_clean
    return lyngsat_dict
    
    
def get_region_urls(link: str) -> list:
    text = requests.get(link).text
    soup = BeautifulSoup(text, 'lxml')
    asia = link + str(soup.find('a', text='Asia', href=True)['href'])
    europe = link + str(soup.find('a', text='Europe', href=True)['href'])
    atlantic = link + str(soup.find('a', text='Atlantic', href=True)['href'])
    america = link + str(soup.find('a', text='America', href=True)['href'])
    return [asia, europe, atlantic, america]


def get_satellite_urls(url: str) -> dict:
    try:
        response = requests.get(url, timeout=20, allow_redirects=False)
        response.raise_for_status()
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
            href_dict = dict([(k,val) for k,val in href_sub.items() if "." not in k])
            # convert hrefs to urls
            for k, val in href_dict.items():
                href_dict[k] = "https://www.lyngsat.com/" + val
            return href_dict
    except HTTPError as hp:
        print(hp)


def get_key_tables(url: str) -> list:
    response = requests.get(url, timeout=20)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'lxml')
        key_tables = []
        for table in soup.find_all('table'):
            text = table.text
            # smart search for table of interest, no class or tags to search by
            string_check = "https://www.lyngsat.com/" 
            if (string_check in text):
                # only the bigtable has a class
                if not table.has_attr("class"):
                    key_tables.append(table)
        return key_tables


def read_tables(sat_name: str, html_tables: list) -> list:
    tables = []
    # table is in html
    for table in html_tables:
        rows = table.find_all('tr')
        num_rows = len(rows)
        # set col num but we only care about cols 1,2,and 4
        num_cols = 10
        # replace table breaks with new lines
        for br in table.find_all('br'):
            br.replace_with("\n")
        # instantialize empty df
        df = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
        
        rep_col = 1
        # handle multi-row columns
        for i, row in enumerate(rows):
            try:
                col_stat = df.iloc[i, :][df.iloc[i, :].isnull()].index[0]
            except IndexError:
                print(i, row)

            for j, cell in enumerate(row.find_all(['td', 'th'])):
                rep_row = get_row_spans(cell)
                # find first non-na col and fill that one
                while any(df.iloc[i, col_stat:col_stat+rep_col].notnull()):
                    col_stat += 1

                # check if <i> is a child of cell
                children = cell.findChildren()
                for child in children:
                    # add asterik to signal text was originally in italics; this is key for separating columns
                    if child.find('i'):
                        df.iloc[i:i+rep_row, col_stat:col_stat+rep_col] = cell.getText() + '*'
                        break
                    else:
                        df.iloc[i:i+rep_row, col_stat:col_stat+rep_col] = cell.getText()
                        break
                if col_stat < df.shape[1]-1:
                    col_stat += rep_col
                    
        tables.append(df)
    
    tables_clean, tables_drop = clean_tables(sat_name, tables)
    
    yellow = "background:#ffffbb"
    green = "background:#bbffbb"
    
    if tables_drop:
        for ele in tables_drop:
            html_tables.pop(ele)
    
    # get html for Provider Name/Channel Name column of interest only
    html_columns = []
    for table in html_tables:
        col_entries = []
        # get table rows
        rows = table.find_all("tr")
        # for each row grab column entry cell 
        for r in rows:
            cell = r.find_all("td")
            # header/footer condition
            if len(cell) > 1:
                # cond for multirow 
                if len(cell) == 8:
                    col_entries.append(cell[1])
                #cond for singular row
                elif len(cell) == 10:
                    col_entries.append(cell[3])
        # drop first entry as it is column name
        html_columns.append(col_entries[1:])

    #loop through html columns
    for h, col in enumerate(html_columns):
        table_star = tables_clean[h]
        # loop through channel name values in a given table
        for m in range(0, len(table_star['Channel Name'].values)):
            cell = col[m]
            channel_status = cell["style"]
            if (channel_status == green) or (channel_status == yellow):
                table_star.loc[m, "Channel On"] = "ON"
            else:
                table_star.loc[m, "Channel On"] = "OFF"
    
    return tables_clean


def get_row_spans(cell) -> int:
    if cell.has_attr('rowspan'):
        rep_row = int(cell.attrs['rowspan'])
    else:
        rep_row = 1
    return rep_row


def clean_tables(sat_name: str, df_tables: list) -> list:
    clean_tables = []
    drop_tables = []
    for k, df in enumerate(df_tables):
        # drop all columns except 0, 1, and 3 corresponding to 1, 2, and 4
        df_clean = df.iloc[:, [0, 1, 3]]
        # drop headers and footer 
        df_clean.drop(index=[df_clean.index[0], df_clean.index[1]], axis=0, inplace=True)
        df_clean.drop(index=df_clean.index[-1], axis=0, inplace=True)
        
        # check for empty table
        if df.empty:
            drop_tables.append(k)
            continue
        else:
            df_clean.reset_index(drop=True, inplace=True)
        
            # instantiate empty clean dataframe with desired columns 
            df_new = pd.DataFrame(np.ones((len(df_clean), 11))*np.nan, columns=['Satellite', 'Frequency', 'Transponder', 'Beam', 'EIRP (dBW)', 
                'System', 'SR', 'FEC', 'Provider Name', 'Channel Name', 'Channel On'])
            
            # populate Satellite col
            df_new.loc[df_new.index, "Satellite"] = sat_name
            
            # iterate through rows with same info for col 0
            rows = df_clean[0].unique()
            for val in rows:
                df_temp = df_clean.loc[df_clean[0].isin([val])]
                # split column 0 
                col0_value = df_temp.iloc[0, 0]
                split0_value = col0_value.split("\n")
                for split in split0_value:
                    if "tp" in split:
                        df_new.loc[df_temp.index, "Transponder"] = split
                        continue
                    elif any(s.isdigit() for s in split) == False:
                        df_new.loc[df_temp.index, "Beam"] = split
                        continue
                    elif ("L" in split) or ("R" in split) or ("H" in split) or ("V" in split):
                        df_new.loc[df_temp.index, "Frequency"] = split
                        continue
                    else:
                        if "*" in split:
                            split = split.replace("*", "")
                        df_new.loc[df_temp.index, "EIRP (dBW)"] = split
                # split column 1
                col1_value = df_temp.iloc[0, 1]
                split1_value = col1_value.split("\n")
                for split in split1_value:
                    if "/" in split:
                        df_new.loc[df_temp.index, "FEC"] = split
                        continue
                    elif all(s.isdigit() for s in split):
                        df_new.loc[df_temp.index, "SR"] = split
                        continue
                    else:
                        if df_new.loc[df_temp.index, "System"].isnull().values.all():
                            df_new.loc[df_temp.index, "System"] = split
                        else:
                            df_new.loc[df_temp.index, "System"] = df_new.loc[df_temp.index, "System"].astype(str) + " " + split
                for i in range(0, len(df_temp)):
                    # split column 2
                    test_string = df_temp.iloc[i, 2]
                    if "*" in test_string:
                        new_string = test_string.replace("*", "")
                        df_new.loc[df_temp.index, "Provider Name"] = new_string
                    else:
                        df_new.loc[df_temp.index[i], "Channel Name"] = test_string
            clean_tables.append(df_new)
    return clean_tables, drop_tables
    

def save_tables(path: Path, dict_: dict):
    df = pd.DataFrame(dict_)
    df.to_csv(path / 'lyngsat.csv', index=False)

