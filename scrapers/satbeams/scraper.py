from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import pickle

class scraper():
    def __init__(self):
        pass

    def get_front_page_html(self):
        url = 'https://satbeams.com/satellites?status=active'
        html = requests.get(url).text
        self.front_page_soup = BeautifulSoup(html, features='html.parser')


    def parse_front_page_soup(self):
        table_rows = self.front_page_soup.find('table', {'id': 'sat_grid'}).find_all('tr')
        table_headers = [th.get_text(strip=True) for th in table_rows[0]]
        self.front_page_table = pd.DataFrame(columns=table_headers)

        for tr in table_rows[1:]:
            row_ind = len(self.front_page_table)
            new_row = [td.get_text(strip=True) for td in tr.find_all('td')]
            self.front_page_table.loc[row_ind] = new_row

        keep_cols = ['Position', 'Satellite Name', 'Norad', 'Cospar', 'Operator', 'Comments']
        self.front_page_table = self.front_page_table.loc[:, keep_cols]
        print(self.front_page_table)

    def get_beam_maps(self):
        self.beam_url_dict = dict()
        for id in self.front_page_table['Norad'][:5]:
            url = 'https://satbeams.com/satellites?norad='+id
            html = requests.get(url).text
            self.beam_url_dict[id] = re.findall('beam=(.+?)"', html)

            with open('scrapers/satbeams/outputs/norad_beam_dict.pkl', 'wb') as handle:
                pickle.dump(self.beam_url_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print(self.beam_url_dict)






scraper = scraper()
scraper.get_front_page_html()
scraper.parse_front_page_soup()
scraper.get_beam_maps()