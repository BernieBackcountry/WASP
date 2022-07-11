import pandas as pd
from urllib.request import urlopen

data = urlopen('https://celestrak.com/NORAD/elements/geo.txt').read().decode('utf-8')
data = data.split('\r\n')

for i, item in enumerate(data):
    data[i] = " ".join(data[i].split())

data_list = list(data)
sat_id = []
table_body = []
for i in range(0, len(data_list)):
    if i % 3 == 0:
        sat_id.append(data_list[i])
        sat_id.append(data_list[i])
    else:
        table_body.append(data_list[i])

while "" in sat_id:
    sat_id.remove("")

df = pd.DataFrame([sub.split(' ') for sub in table_body])
master_table = pd.concat([pd.Series(sat_id), df], axis=1)
master_table.to_csv('C:/Users/lexi.denhard/Documents/Celestrak-Satellite-Data2.csv', encoding='utf-8', index=False)

# looked at website; there is a way to generalize the web-scraper if need be
