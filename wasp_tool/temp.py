from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import itertools
import re

import wasp_tool.utilities as utilities


def get_region_urls(link: str) -> list:
    text = requests.get(link).text
    soup = BeautifulSoup(text, 'lxml')
    asia = link + str(soup.find('a', text='Asia', href=True)['href'])
    europe = link + str(soup.find('a', text='Europe', href=True)['href'])
    atlantic = link + str(soup.find('a', text='Atlantic', href=True)['href'])
    america = link + str(soup.find('a', text='America', href=True)['href'])
    return [asia, europe, atlantic, america]


def get_lyngsat_info(region_urls: list) -> dict:
    lyngsat_dict = {}
    for region in region_urls:
        print(region)
        # dict sat names and href for each region
        #sat_dict = get_satellite_urls(region)
        sat_dict = {'NSS 9': "https://www.lyngsat.com/NSS-9.html"}
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
        print(url)
        return key_tables


def read_tables(sat_name: str, html_tables: list) -> list:
    tables = []
    df_channel_status = []
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
    
    for h, table in enumerate(html_tables):
        table_star = tables_clean[h]
        # loop through channel name values in a given table
        for m, channel in enumerate(table_star['Channel Name'].values):
            # check for string value
            if (isinstance(channel, str)) and (channel != "\n"):
                print(channel)
                # get html for channel cell
                cell = table.find('td', text=channel)
                print(cell)
                # determine colorbox surrounding cell
                if cell is not None:
                    colorbox = cell["style"]
                    print(colorbox)
                    if (colorbox == green) or (colorbox == yellow):
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
                

# TODO: channel is ON aka yellow or green 

yellow_box = "background:ffffbb"
green_box = "background:bbffbb"
# potentially drop rows without channel name? Ask 16th about this

main_page = 'https://www.lyngsat.com/'

# obtain satellite regions
region_urls = get_region_urls(main_page)

lyngsat_dict = get_lyngsat_info([region_urls[0]])
print(lyngsat_dict.keys())
print(lyngsat_dict['NSS 9'])
print(lyngsat_dict['JCSAT 4B'])
# its cause band has and in it; need to rethink delimeter
print(lyngsat_dict['Superbird B3'])
