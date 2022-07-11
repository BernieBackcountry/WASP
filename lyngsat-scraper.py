from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import itertools


def get_url_content(link):
    """
    INPUT:
        1. html link to lyngsat page of interest
    OUTPUT:
        1. BeautifulSoup object
    """
    html_text = requests.get(link).text
    bsoup = BeautifulSoup(html_text, 'html5lib')
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
        # Check if we can split into three
        temp_df = df['Frequency\nBeam\nEIRP (dBW)'].str.split('\n', expand=True)
        if len(temp_df.columns) == 2:
            df[['Frequency', 'EIRP (dBW)']] = df['Frequency\nBeam\nEIRP (dBW)'].str.split('\n', 1, expand=True)
            df['Beam'] = np.nan
        elif len(temp_df.columns) == 1:
            df['Frequency'] = df['Frequency\nBeam\nEIRP (dBW)']
            df['Beam'] = np.nan
            df['EIRP (dBW'] = np.nan
        elif len(temp_df.columns >= 3):
            df[['Frequency', 'Beam,', 'EIRP (dBW)']] = df['Frequency\nBeam\nEIRP (dBW)'].str.split('\n', 2, expand=True)
        else:
            print('Error in splitting columns')
            print('number of possible splits')
            print(len(temp_df.columns))
        df.drop(columns=['Frequency\nBeam\nEIRP (dBW)'], inplace=True)

        # temp_df = df['System\nSR\nFEC'].str.split('\n', 2, expand=True)
        # if len(temp_df.columns) != 3:

        # else:
        #  df[['System', 'SR', 'FEC']] = df['System\nSR\nFEC'].str.split('\n', 2, expand=True)

        # df[['System', 'SR', 'FEC']] = df['System\nSR\nFEC'].str.split('\n', 2, expand=True)
        # df.drop(columns=['System\nSR\nFEC', '\n'], inplace=True)

        df.replace('\n', ' ', regex=True, inplace=True)
        df.columns = df.columns.str.replace('\n', ' ', regex=True)
        tables_clean.append(df)
    return tables_clean


asia = 'https://www.lyngsat.com/asia.html'
europe = 'https://www.lyngsat.com/europe.html'
atlantic = 'https://www.lyngsat.com/atlantic.html'
america = 'https://www.lyngsat.com/america.html'
satellites = [asia, europe, atlantic, america]

all_urls = []
for n in range(0, len(satellites)):
    all_urls += get_urls(satellites[n])

final_tables = []
for p in range(0, len(all_urls)):
    soup = get_url_content(all_urls[p])
    tables = get_key_tables(soup)
    dfs = read_table(tables)
    if not dfs:
        continue
    dfs_clean = clean_table(dfs)
    final_tables.append(dfs_clean)

final_dfs = list(itertools.chain.from_iterable(final_tables))
column_names = ['Frequency',
                'Beam',
                'EIRP (dBW)',
                'System SR FEC',
                'Logo SID',
                'Provider Name Channel Name',
                'ONID-TID Compression Format',
                'VPID',
                'C/N lock audio',
                'Encryption',
                'Source Updated ']

for k in range(0, len(final_dfs)):
    final_dfs[k] = final_dfs[k].reindex(columns=column_names)

master_table = pd.concat(final_dfs)
master_table.to_csv('C:/Users/lexi.denhard/Documents/Lyngsat-Satellite-Data.csv', encoding='utf-8', index=False)
