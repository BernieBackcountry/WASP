import pandas as pd
import threading
from tqdm import tqdm
import requests
from io import BytesIO
import pypdfium2 as pdfium
import shutil
import time


def standardize_satellite(sat_name: str) -> str:
    # strip end parenthesis 
    name_replace = sat_name.replace(")", "")
    # strip leading/following spaces
    name_strip = name_replace.strip()

    # cast whole string to upper
    name_upper = name_strip.upper()

    # ALTERVISTA SPECIFIC ONE-OFF CASES
    # if "TÃ¼RKMENÃLEM" in name_upper():
    #     name_upper = name_upper.replace("TÃ¼RKMENÃLEM", "TURKMENÄLEM")

    if "TURKSAT" in name_upper:
        name_upper = name_upper.replace("TURKSAT", "TÜRKSAT")
    
    if ("INTELSA") in name_upper and ("INTELSAT" not in name_upper):
        name_upper = name_upper.replace("INTELSA", "INTELSAT")

    # CASE 1: replacing sub-strings for consistency
    case_1 = {"G-SAT": "GSAT", 
        "HELLASSAT": "HELLAS SAT", 
        "HELLAS-SAT": "HELLAS SAT", 
        "HOTBIRD": "HOT BIRD"}
    for substring in case_1.keys():
        if substring in name_upper:
            name_upper = name_upper.replace(substring, case_1[substring])
            break

    # CASE 2: hot birds are eutelsats
    if ("HOT BIRD" in name_upper) and ("EUTELSAT" not in name_upper):
        name_upper = name_upper.replace("HOT BIRD", "EUTELSAT HOT BIRD")
    
    # CASE 3: replacing white space with dashes
    dash_add = ["ABS", "AMC", "AMOS", "ARABSAT", "ATHENA FIDUS", "BADR", "BSAT", "BEIDOU ", 
        "BULGARIASAT", "CIEL", "CMS", "EXPRESS AT", "EXPRESS AM", "GSAT", "HORIZONS", "INSAT", 
        "JCSAT", "KAZSAT", "MEASAT", "NSS", "PAKSAT", "PSN", "SES", "TKSAT", "VIASAT", "VINASAT", 
        "WILDBLUE", "XM "]
    if (any(substring in name_upper for substring in dash_add)) and ("SERIES" not in name_upper):
        name_upper = name_upper.replace(" ", "-", 1)
    
    # CASE 4: replacing dashes with white space
    dash_remove = ["EXPRESS AMU", "THURAYA"]
    if any(substring in name_upper for substring in dash_remove):
        name_upper = name_upper.replace("-", " ", 1)

    new_name = name_upper
    return new_name


def save_dict_to_csv(aws_bucket: str, dict_: dict, key: str):
    df = pd.DataFrame(dict_)
    # write csv to s3 bucket
    df.to_csv(f"s3://{aws_bucket}/data/{key}", index=False)


def save_footprints(aws_client, aws_bucket: str, sat_names: list, footprints: list):
    images, titles = map(list, zip(*footprints))
    jobs = []
    for k, sat in enumerate(sat_names):
        thread = threading.Thread(target=image_download, args=(aws_client, aws_bucket, sat, images, titles, k))
        jobs.append(thread)

    for j in jobs:
        threads = threading.active_count()
        while threads > 4:
            time.sleep(5)
            threads = threading.active_count()
        j.start()
    for j in jobs:
        j.join()

    
def image_download(aws_client, aws_bucket: str, sat_name: str, image_links: list, image_titles: list, iter: int):
    sat_images = image_links[iter]
    sat_titles = image_titles[iter]
    file_path = 'data/footprints/' + sat_name + '/'
    # download and save images 
    for i, image in tqdm(enumerate(sat_images)):
        jpg_name = sat_titles[i] + ".jpg"
        try:
            r = requests.get(image, stream=True, timeout=20)
            if r.status_code == 200:
                r.raw.decode_content = True
                in_mem_file = BytesIO()
                shutil.copyfileobj(r.raw, in_mem_file)
                in_mem_file.seek(0)
                aws_client.put_object(Body=in_mem_file, Bucket=aws_bucket, Key=file_path + jpg_name)
                r.close()
                print("Image download successful")
        except:
            print("Unable to download image", sat_name, jpg_name)
            pass 


def save_tables(aws_bucket: str, dict_: dict):
    for key, lst in dict_.items():
        # / causes problem with directory name
        if "/" in key:
            key = key.replace("/", "-")
        for i, ele in enumerate(lst): 
            key_final = key + "/" + key + "_" + str(i) + ".csv"
            ele.to_csv(f"s3://{aws_bucket}/data/channels/{key_final}", index=False)


def save_pdfs(aws_client, aws_bucket: str, names: list, urls: list):
    for i, url in enumerate(urls):
        sat_name = names[i]
        file_path = 'data/freq_plans/' + sat_name + '/'
        #try:
        req = requests.get(url)
        req.close()
        pdf_name = sat_name + ".pdf"
        # write pdf to s3 bucket
        aws_client.put_object(Body=req.content, Bucket=aws_bucket, Key=file_path + pdf_name)
        # read pdf from s3 bucket
        obj = aws_client.get_object(Bucket=aws_bucket, Key=file_path + pdf_name)['Body'].read()
        pdf = pdfium.PdfDocument(BytesIO(obj))

        n_pages = len(pdf)
        # save pdf as new jpg
        try:
            for i in range(n_pages):
                jpg_name = sat_name + "_" + str(i) + ".jpg"
                page = pdf[i]
                in_mem_file = BytesIO()
                pil_image = page.render(scale=2).to_pil()
                pil_image.save(in_mem_file, format="JPEG")
                in_mem_file.seek(0)
                aws_client.put_object(Body=in_mem_file, Bucket=aws_bucket, Key=file_path + jpg_name)
            
                print("File", sat_name, "downloaded successfully")
        except:
            print("Unable to download", sat_name)
            pass
