#Start on active satellites webpage, click links to each satellite, download jpgs of footprints, tag all info to satellite, return to active satellite webpage, and repeat
import requests
from bs4 import BeautifulSoup

url = 'https://satbeams.com/satellites?status=active'
headers = {'User-Agent': 'Chrome/51.0.2704.103'}
page = requests.get(url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')

for link in soup.findAll('a', {'class': 'link'}):
    try:
        print ("https://satbeams.com/"+str((link['href'])))
    except KeyError:
        pass

#For each individual satellite page, identifies the link for the footprint images. Downloading images not working yet
#start on active satellite page, get all href of a tags, which are a child of a td tag
#<a class="link" href="/satellites?norad=39773">Eutelsat 3B (E3B)</a>
links = [link['href=']]

def extract_image_links(webpage, headers):
    # Send GET request
    response = requests.get(webpage, headers=headers)
    
    # Check if the status_code is 200
    if response.status_code == 200:
        
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all of the image tags:
        images = soup.findAll('img')
        
        # Extract 'src' attribute of every image
        image_links = []
        for image in images:
            image_links.append(image.attrs['src'])
        
        #Filter for JPG format image links
        image_links = [image for image in image_links if image.endswith('.jpg')]
        return image_links
if __name__ == "__main__":
    
    # Define HTTP Headers
    headers = {"User-Agent": "Chrome/51.0.2704.103",}
    # Define URL of the webpage
    webpage = 'https://satbeams.com/satellites?norad=36033'
    #Extract image links
    image_links = extract_image_links(webpage, headers)
    
    print(image_links)
 
       
     # Download all images - NOT WORKING
    for i, url in enumerate(image_links):
        file_name = f'image_{i}.jpg'
        download_image(url, file_name, headers)
