import requests
from bs4 import BeautifulSoup
import threading
import queue


def prepare_satbeams(url: str) -> dict:
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    # get all active satellite url pages
    urls = get_active_sat_urls(soup)
    satbeams_info, footprints = run_threads(soup, urls)
    return satbeams_info, footprints
  

def get_active_sat_urls(soup: BeautifulSoup) -> list:
    urls = []
    for link in soup.findAll('a', {'class': 'link'}):
        urls.append("https://satbeams.com"+str((link['href'])))
    return urls
    

def run_threads(soup: BeautifulSoup, urls: list) -> list:
    sat_info = []
    sat_footprints = []
    q_info = queue.Queue()
    #q_footprints = queue.Queue()
    
    threads = [threading.Thread(target=fetch_url, args=(url, q_info)) for url in urls] #, q_footprints
    for thread in threads:
        thread.start()
        # Get satellite info
        info = q_info.get()
        sat_info.append(info)
        print("Thread")
        # Get satellite footprints
        #footprints = q_footprints.get()
        #if footprints is None:
            # append empty nested list for None footprints case
        #    lst = [[] for _ in range(2)]
        #    sat_footprints.append(lst)
        #else:
        #    sat_footprints.append(footprints)
    for thread in threads:
        thread.join()
        
    sat_dict = list_to_dict(sat_info)
    return sat_dict, sat_footprints


def fetch_url(url: str, q1: queue.Queue): #, q2: queue.Queue):
    try:
        response = requests.get(url, timeout=20)
        # Check if the status_code is 200
        if response.status_code == 200:    
            # Parse the HTML content of the webpage
            soup = BeautifulSoup(response.content, 'html.parser')
            # Scrap satellite info
            sat_info = get_satellite_info(soup)
            # Put satellite info on queue
            q1.put(sat_info)
            # Scrap footprints
            #sat_footprints = get_satellite_footprints(soup)
            # Put footprints info on queue
            #q2.put(sat_footprints)
    except Exception as e:
        print(url)
        pass


def get_satellite_info(soup: BeautifulSoup) -> list:
    sat = find_by_label(soup, "Satellite Name:")
    if "(" in sat:
        temp = sat.split("(", 1)
        sat_name = temp[0].strip() # don't cast to upper
        temp_2 = temp[1].strip()
        sat_name_excess = temp_2[:-1]
    else:
        sat_name = sat.strip()
        sat_name_excess = ""
    position = str(find_by_label(soup, "Position:"))
    norad_id = str(find_by_next(soup, "NORAD:", "a").contents[0])
    beacons = str(find_by_label(soup, "Beacon(s):"))
    return [sat_name, sat_name_excess, position, norad_id, beacons]


def find_by_label(soup: BeautifulSoup, label: str) -> str:
    span = soup.find("b", text=label)
    if span:
        return str(span.next_sibling)
    else:
        return ""


def find_by_next(soup: BeautifulSoup, label: str, tag: str) -> str:
    span = soup.select("b", text=label)[0]
    return span.find_next(tag)


def get_satellite_footprints(soup: BeautifulSoup) -> list:
    # Find all of the appropriate image tags:
    temp = soup.find('div', {'id': 'sliderDiv'})
    if temp is not None:
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
        tag = 'https://satbeams.com'
        images = [tag+i for i in image_links]
        return [images, image_titles]
    
    
def list_to_dict(results: list) -> dict:
    sat_name, sat_name_excess, pos, nor, beac = ([] for i in range(5))
    for ele in results:
        sat_name.append(ele[0])
        sat_name_excess.append(ele[1])
        pos.append(ele[2])
        nor.append(ele[3])
        beac.append(ele[4])
        
    dict_ = {'Satellite': sat_name,
            'Extra Names': sat_name_excess,
            'Position': pos,
            'NORAD ID': nor, 
            'Beacons': beac}
    
    return dict_
