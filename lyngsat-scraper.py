from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import itertools
import re


def get_url_content(link):
    """
    INPUT:
        1. html link to lyngsat page of interest
    OUTPUT:
        1. BeautifulSoup object
    """
    html_text = requests.get(link).text
    bsoup = BeautifulSoup(html_text, 'lxml')
    return bsoup


def get_urls(link):
    """
    INPUT:
        1. html link to main lyngsat page of interest i.e. (Satellite Main Page for Asia)
    OUTPUT:
        1. list of hyperlinks for subpages off the main page
    """
    bsoup = get_url_content(link)

    href_temp = []
    for href in bsoup.find_all('a', href=True):
        href_temp.append(href['href'])

    string_search = "http"
    temp = [string for string in href_temp if string_search not in string]
    string_add = "https://www.lyngsat.com/"
    href_list = [string_add + s for s in temp]
    return href_list


def get_key_tables(bsoup):
    """
    INPUT:
        1. BeautifulSoup object
    OUTPUT:
        1. list of key tables in html representation
    """
    key_tables = []
    for index, table in enumerate(bsoup.find_all('table')):
        text = table.text
        string_check = "https://www.lyngsat.com/"
        if (string_check in text) and (index != 0):
            key_tables.append(table)
            continue
    return key_tables


def get_row_spans(cell):
    """
    INPUT:
        1. cell - a <td>...</td> element that contains a table cell entry
    OUTPUT:
        1. tuple with the cell's row spans
    """
    if cell.has_attr('rowspan'):
        rep_row = int(cell.attrs['rowspan'])
    else:
        rep_row = 1
    return rep_row


def read_table(tables):
    """
    INPUT:
        1. list of tables in html representation
    OUTPUT:
        1. list of dataframes; one dataframe corresponds to one key table
    """
    dataframes = []
    for m in range(0, len(tables)):
        table = tables[m]

        for br in table.find_all('br'):
            br.replace_with("\n")

        table_rows = table.find_all('tr')
        num_rows = len(table_rows)
        num_cols = 10

        df = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
        rep_col = 1
        for i, row in enumerate(table_rows):
            try:
                col_stat = df.iloc[i, :][df.iloc[i, :].isnull()].index[0]
            except IndexError:
                print(i, row)

            for j, cell in enumerate(row.find_all(['td', 'th'])):
                rep_row = get_row_spans(cell)

            # find first non-na col and fill that one
                while any(df.iloc[i, col_stat:col_stat+rep_col].notnull()):
                    col_stat += 1

                df.iloc[i:i+rep_row, col_stat:col_stat+rep_col] = cell.getText()
                if col_stat < df.shape[1]-1:
                    col_stat += rep_col
        temp = df.iloc[-1].values[0]
        df.drop(index=df.index[0], axis=0, inplace=True)
        df.drop(index=df.index[-1], axis=0, inplace=True)
        df.columns = df.iloc[0]
        df = df[1:]
        if not df.empty:
            dataframes.append(df)
    return dataframes


def clean_table(tables):
    """
    INPUT:
        1. list of dataframes
    OUTPUT:
        1. list of cleaned dataframes
    """
    tables_clean = []
    for i in range(0, len(tables)):
        df = tables[i]
        df.replace('\n', ' ', regex=True, inplace=True)
        df.columns = df.columns.str.replace('\n', ' ', regex=True)
        tables_clean.append(df)
    return tables_clean


asia = 'https://www.lyngsat.com/asia.html'
#europe = 'https://www.lyngsat.com/europe.html'
#atlantic = 'https://www.lyngsat.com/atlantic.html'
#america = 'https://www.lyngsat.com/america.html'
satellites = [asia] #, europe, atlantic, america]

all_urls = []
for n in range(0, len(satellites)):
    all_urls += get_urls(satellites[n])
    
temp = set(all_urls)
all_urls = list(temp)

satellites_list = []
final_tables = []
for p in range(0, len(all_urls)):
    url = all_urls[p]
    soup = get_url_content(url)
    tables = get_key_tables(soup)
    dfs = read_table(tables)
    if not dfs:
        continue
    dfs_clean = clean_table(dfs)
    sat = re.search('https://www.lyngsat.com/(.*).html', url).group(1).replace("-", " ")
    satellites_list.append(sat)
    final_tables.append(dfs)

final_dfs = list(itertools.chain.from_iterable(final_tables))
column_names = ['Frequency Beam EIRP (dBW)',
                'System SR FEC',
                'Logo SID',
                'Provider Name Channel Name',
                'ONID-TID Compression Format',
                'VPID',
                'C/N lock audio',
                'Encryption',
                'Source Updated ']

print(satellites_list)
for k in range(0, len(final_dfs)):
    final_dfs[k] = final_dfs[k].reindex(columns=column_names)
    final_dfs[k].insert(0, 'Satellite', satellites_list[k]*len(final_dfs[k].index))

master_table = pd.concat(final_dfs)
#print(master_table)
master_table.to_csv('Lyngsat-sats.csv', encoding='utf-8-sig', index=False)
