import requests
from bs4 import BeautifulSoup
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

import wasp_tool.utilities as utilities


def prepare_lyngsat(url: str) -> dict:
    region_urls = get_region_urls(url)
    master_dict = {}
    priSatNames, secSatNames = ([] for i in range(2))
    for region in region_urls:
        # dict sat names and href for each region
        sat_dict = get_satellite_urls(region)
        # loop through each regional satellite
        for key, val in sat_dict.items():
            if "(" in key:
                temp = key.split("(", 1)
                pri_sat = utilities.standardize_satellite(temp[0])
                priSatNames.append(pri_sat)
                secSatNames.append(utilities.standardize_satellite(temp[1]))
            else:
                pri_sat = utilities.standardize_satellite(key)
                priSatNames.append(pri_sat)
                secSatNames.append("")
            attempts = 10
            for i in range(attempts):
                #try:
                    # send in url 
                key_tables = get_key_tables(val)
                    # check for empty pages
                if key_tables:
                    tables_clean = read_tables(pri_sat, key_tables)
                    master_dict[pri_sat] = tables_clean
                print("Attempt", i+1, "successful for", key)
                
                if i==3:
                    exit(0)
                break
                #except:
                #    print("Attempt", i+1, "unsuccessful for", key)
                #    pass

    dict_ = {'priSatName': priSatNames,
             'secSatName': secSatNames}
    return dict_, master_dict
    
    
def get_region_urls(link: str) -> list:
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'lxml')
    regions = ["Asia", "Europe", "Atlantic", "America"]
    urls = []
    for r in regions:
        urls.append(link + str(soup.find('a', text=r, href=True)['href']))
    return urls


def get_satellite_urls(url: str) -> dict:
    response = requests.get(url, timeout=20, allow_redirects=False)
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



def get_key_tables(url: str) -> list:
    response = requests.get(url, timeout=30)
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


def read_tables(sat_name: str, html_tables: list) -> pd.DataFrame:
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

    # loop through html columns
    for h, col in enumerate(html_columns):
        table_star = tables_clean[h]
        # loop through channel name values in a given table
        for m in range(0, len(table_star['(Provider) Channel Name'].values)):
            cell = col[m]
            channel_status = cell["style"]
            if (channel_status == green) or (channel_status == yellow):
                table_star.loc[m, "Channel Status"] = "ON"
            else:
                table_star.loc[m, "Channel Status"] = "OFF"
                
    
    # combine all tables into one large one        
    master_table = pd.concat(tables_clean, ignore_index=True)
    # drop excess rows
    master_table = clean_rows(master_table)
    
    return master_table


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
            df_new = pd.DataFrame(np.ones((len(df_clean), 9))*np.nan, columns=['(Provider) Channel Name', 'Channel Status', 
                    'Frequency', 'System', 'SR', 'FEC', 'Transponder', 'Beam', 'EIRP (dBW)'])
            
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
                            
                new_string = ""
                for i in range(0, len(df_temp)):
                    # split column 2
                    test_string = df_temp.iloc[i, 2]
                    if "*" in test_string:
                        new_string = test_string.replace("*", "")
                        df_new.loc[df_temp.index, "(Provider) Channel Name"] = "(" + new_string + ")"
                    else:
                        if new_string == "":
                            df_new.loc[df_temp.index[i], "(Provider) Channel Name"] = test_string
                        else:
                            df_new.loc[df_temp.index[i], "(Provider) Channel Name"] = "(" + new_string + ") " + test_string
                            
            clean_tables.append(df_new)
    return clean_tables, drop_tables
    
    
def clean_rows(table: pd.DataFrame) -> pd.DataFrame:
    # drop blank/unnecessary rows based on provider/channel condition
    drop = []
    for row in range(len(table)):
        row_val = table['(Provider) Channel Name'].iloc[row]
        # check for \n rows 
        if "\n" in str(row_val):
            drop.append(row)
        # check for NaN rows
        if pd.isnull(row_val):
            drop.append(row)
        # check for provider only rows 
        value = row_val.strip()
        if (value.rfind("(") == 0) and (value.rfind(")") == (len(value)-1)):
            drop.append(row)   
        # can add something to check for feeds etc.
        if value in ['test card', 'info card', 'feeds']:
            drop.append(row)
            
    table.drop(drop, axis=0, inplace=True) 
    return table
