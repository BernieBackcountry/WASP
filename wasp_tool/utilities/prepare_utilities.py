import pickle
import queue
import shutil
import threading
import time
from io import BytesIO

import pandas as pd
import pypdfium2 as pdfium
import requests
from PIL import Image
from tqdm import tqdm


def standardize_satellite(sat_name: str) -> str:
    # strip end parenthesis 
    name_replace = sat_name.replace(')', '')
    # strip leading/following spaces
    name_strip = name_replace.strip()

    # cast whole string to upper
    name_upper = name_strip.upper()

    # ALTERVISTA SPECIFIC ONE-OFF CASES
    # if 'TÃ¼RKMENÃLEM' in name_upper():
    #     name_upper = name_upper.replace('TÃ¼RKMENÃLEM', 'TURKMENÄLEM')

    if 'TURKSAT' in name_upper:
        name_upper = name_upper.replace('TURKSAT', 'TÜRKSAT')
    
    if ('INTELSA') in name_upper and ('INTELSAT' not in name_upper):
        name_upper = name_upper.replace('INTELSA', 'INTELSAT')

    # CASE 1: replacing sub-strings for consistency
    case_1 = {'G-SAT': 'GSAT', 
        'HELLASSAT': 'HELLAS SAT', 
        'HELLAS-SAT': 'HELLAS SAT', 
        'HOTBIRD': 'HOT BIRD'}
    for substring in case_1.keys():
        if substring in name_upper:
            name_upper = name_upper.replace(substring, case_1[substring])
            break

    # CASE 2: hot birds are eutelsats
    if ('HOT BIRD' in name_upper) and ('EUTELSAT' not in name_upper):
        name_upper = name_upper.replace('HOT BIRD', 'EUTELSAT HOT BIRD')
    
    # CASE 3: replacing white space with dashes
    dash_add = ['ABS', 'AMC', 'AMOS', 'ARABSAT', 'ATHENA FIDUS', 'BADR', 'BSAT', 'BEIDOU ', 
        'BULGARIASAT', 'CIEL', 'CMS', 'EXPRESS AT', 'EXPRESS AM', 'GSAT', 'HORIZONS', 'INSAT', 
        'JCSAT', 'KAZSAT', 'MEASAT', 'NSS', 'PAKSAT', 'PSN', 'SES', 'TKSAT', 'VIASAT', 'VINASAT', 
        'WILDBLUE', 'XM ']
    if (any(substring in name_upper for substring in dash_add)) and ('SERIES' not in name_upper):
        name_upper = name_upper.replace(' ', '-', 1)
    
    # CASE 4: replacing dashes with white space
    dash_remove = ['EXPRESS AMU', 'THURAYA']
    if any(substring in name_upper for substring in dash_remove):
        name_upper = name_upper.replace('-', ' ', 1)

    new_name = name_upper
    return new_name


def save_dict_to_csv(aws_bucket: str, dict_: dict, key: str):
    df = pd.DataFrame(dict_)
    # write csv to s3 bucket
    df.to_csv(f's3://{aws_bucket}/data/{key}', index=False)


def save_footprints(aws_client, aws_bucket: str, sat_names: list, footprints: list):
    encoding_dict = {}
    images, titles = map(list, zip(*footprints))
    q_encod = queue.Queue()
    q_title = queue.Queue()
    jobs = []
    for k, sat in enumerate(sat_names):
        thread = threading.Thread(target=image_download, args=(aws_client, aws_bucket, sat, images, titles, k, q_encod, q_title))
        jobs.append(thread)

    for j in jobs:
        threads = threading.active_count()
        while threads > 4:
            time.sleep(5)
            threads = threading.active_count()
        j.start()
        encodings = q_encod.get()
        encod_titles = q_title.get()
        for i in range(len(encodings)):
            encoding_dict[encod_titles[i]] = encodings[i]
    for j in jobs:
        j.join()
    
    pickle_byte_obj = pickle.dumps(encoding_dict) 
    aws_client.put_object(Body=pickle_byte_obj, Bucket=aws_bucket, Key='data/footprint_encodings.pkl')

    
def image_download(aws_client, aws_bucket: str, sat_name: str, image_links: list, image_titles: list, iter: int, q1: queue.Queue, q2: queue.Queue):
    encodings = []
    titles = []
    sat_images = image_links[iter]
    sat_titles = image_titles[iter]
    # download and save images 
    for i, image in tqdm(enumerate(sat_images)):
        jpg_name = f'{sat_titles[i]}.jpg'
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                r.raw.decode_content = True
                in_mem_file = BytesIO()
                shutil.copyfileobj(r.raw, in_mem_file)
                r.close()
                in_mem_file.seek(0)
                # create image encoding 
                img = Image.open(in_mem_file)
                # add encoding to dict 
                encodings.append(img)
                titles.append(f'{sat_name}/{sat_titles[i]}')
                print("Image download successful")
        except:
            print('Unable to download image', sat_name, jpg_name)
            pass 
    q1.put(encodings)
    q2.put(titles)


def save_tables(aws_bucket: str, dict_: dict):
    for key, val in dict_.items():
        # / causes problem with directory name
        if '/' in key:
            key = key.replace('/', '-')
        key_final = f'{key}/{key}.csv'
        val.to_csv(f's3://{aws_bucket}/data/channels/{key_final}', index=False)


def save_pdfs(aws_client, aws_bucket: str, names: list, urls: list):
    for i, url in enumerate(urls):
        sat_name = names[i]
        file_path = f'data/freq_plans/{sat_name}/'
        try:
            req = requests.get(url)
            req.close()
            pdf_name = f'{sat_name}.pdf'
            # write pdf to s3 bucket
            aws_client.put_object(Body=req.content, Bucket=aws_bucket, Key=file_path + pdf_name)
            # read pdf from s3 bucket
            obj = aws_client.get_object(Bucket=aws_bucket, Key=file_path + pdf_name)['Body'].read()
            pdf = pdfium.PdfDocument(BytesIO(obj))

            n_pages = len(pdf)
            # save pdf as new jpg
            for i in range(n_pages):
                jpg_name = f'{sat_name}_{str(i)}.jpg'
                page = pdf[i]
                in_mem_file = BytesIO()
                pil_image = page.render().to_pil()
                pil_image.save(in_mem_file, format="JPEG")
                in_mem_file.seek(0)
                aws_client.put_object(Body=in_mem_file, Bucket=aws_bucket, Key=file_path + jpg_name)
        
            print('File', sat_name, 'downloaded successfully')
        except:
            print ('File', sat_name, 'unable to download')