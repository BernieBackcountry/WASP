import urllib.request
import pandas as pd

urllib.request.urlretrieve("https://celestrak.com/NORAD/elements/geo.txt", "celestrak-geo.txt")
read_file = pd.read_csv(r'geo.txt')
read_file.to_csv(r'celestrak-geo.csv', index=None)
