import time
import pandas as pd
import threading
from tqdm import tqdm
import requests
import re
# import shutil #save img locally
from bs4 import BeautifulSoup


def find_by_label(soup, label):
    return soup.find("b", text=re.compile(label)).next_sibling


def find_by_next(soup, label, tag):
    span = soup.select("b", text=re.compile(label))[0]
    return span.find_next(tag)


def fetch_url(url):
    global sat_name
    global sat_pos
    global sat_norad
    sat_name = []
    sat_pos = []
    sat_norad = [] 
    response = requests.get(url, headers=headers)
    # Check if the status_code is 200
    if response.status_code == 200:    
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        # SATELLITE INFO SCRAPING 
        sat_name.append(find_by_label(soup, "Satellite Name:"))
        sat_pos.append(find_by_label(soup, "Position:"))
        sat_norad.append(find_by_next(soup, "NORAD:", "a").contents[0])
        # IMAGE SCRAPING 
        # Find all of the image tags:
        images = soup.findAll('img')
        # Extract 'src' attribute of every image
        image_links = []
        for image in images:
            image_links.append(image.attrs['src'])
            #Filter for JPG format image links
            image_links = [image for image in image_links if image.endswith('.jpg')]
            #print(image_links)        
        one = 'https://satbeams.com'
        images =  [one+i for i in image_links]
        #NEXT LOOP THROUGH IMAGES TO DOWNLOAD!
        #to save footprint images on satellite page
        for image in tqdm(images):
            file_name = image.split('/')[-1]
            try:
                r = requests.get(image, stream=True)
                if r.status_code == 200:
                    with open(file_name, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
            except Exception as e:
                pass    
        print("'%s\' fetched in %ss" % (url, (time.time() - start)))


url = 'https://satbeams.com/satellites?status=active'
req = requests.get(url)
soup = BeautifulSoup(req.text, "html.parser")
headers = {"User-Agent": "Chrome/51.0.2704.103",}  

# get all links
urls = []
for link in soup.findAll('a', {'class': 'link'}):
    urls.append("https://satbeams.com"+str((link['href'])))

start = time.time()

threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print("Elapsed Time: %s" % (time.time() - start))

df_sats = pd.DataFrame({'SAT NAME': sat_name,
                        'POSITION': sat_pos,
                        'NORAD': sat_norad})

print(df_sats)
