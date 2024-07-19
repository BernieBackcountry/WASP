"""
This module defines functions for standardizing satelling naming conventions and saving
different file types to the AWS bucket.

FUNCTIONS
    standardize_satellite(sat_name: str)
        Standardizes a satellite name according to pre-defined rules.
    save_dict_to_csv(aws_bucket: str, dict_: dict, key: str)
        Saves dictionary to a csv file in the AWS bucket.
    save_footprints(
        aws_client: botocore.client,
        aws_bucket: str,
        sat_names: list,
        footprints: list
    )
        Saves satbeams footprints to the AWS bucket.
    image_download(
        sat_name: str,
        image_links: list,
        image_titles: list,
        iter: int,
        queue_for_image_encodings: queue.Queue,
        queue_for_image_titles: queue.Queue,
    )
        Download footprint images.
    save_tables(aws_bucket: str, dict_: dict)
        Saves lyngsat channels tables to the AWS bucket.
    save_pdfs(
        aws_client: botocore.client,
        aws_bucket: str,
        names: list,
        urls: list
    )
        Saves altervista frequency plans to the AWS bucket.
"""
import json
import pickle
import queue
import shutil
import threading
import time
from io import BytesIO

import botocore
import pandas as pd
import requests
from PIL import Image
from tqdm import tqdm
import numpy as np
import boto3

# define http response success
HTTP_SUCCESS = 200


def standardize_satellite(sat_name: str) -> str: #FIX ME
    """
    Standardizes a satellite name according to pre-defined rules.

    These rules were compiled from knowledge of different site nomenclatures.

    Parameters
    ----------
    sat_name: str
        String containing satellite name

    Returns
    -------
    new_name: str
        String containing standardized satellite name
    """
    # strip end parenthesis
    name_replace = sat_name.replace(")", "")
    # strip leading/following spaces
    name_strip = name_replace.strip()

    # cast whole string to upper
    name_upper = name_strip.upper()

    # ALTERVISTA SPECIFIC ONE-OFF CASES
    # if 'TÃ¼RKMENÃLEM' in name_upper():
    #     name_upper = name_upper.replace('TÃ¼RKMENÃLEM', 'TURKMENÄLEM')

    if "TURKSAT" in name_upper:
        name_upper = name_upper.replace("TURKSAT", "TÜRKSAT")

    if ("INTELSA") in name_upper and ("INTELSAT" not in name_upper):
        name_upper = name_upper.replace("INTELSA", "INTELSAT")

    # CASE 1: replacing sub-strings for consistency
    case_1 = {
        "G-SAT": "GSAT",
        "HELLASSAT": "HELLAS SAT",
        "HELLAS-SAT": "HELLAS SAT",
        "HOTBIRD": "HOT BIRD",
    }
    for substring in case_1.keys():
        if substring in name_upper:
            name_upper = name_upper.replace(substring, case_1[substring])
            break

    # CASE 2: hot birds are eutelsats
    if ("HOT BIRD" in name_upper) and ("EUTELSAT" not in name_upper):
        name_upper = name_upper.replace("HOT BIRD", "EUTELSAT HOT BIRD")

    # CASE 3: replacing white space with dashes
    dash_add = [
        "ABS",
        "AMC",
        "AMOS",
        "ARABSAT",
        "ATHENA FIDUS",
        "BADR",
        "BSAT",
        "BEIDOU ",
        "BULGARIASAT",
        "CIEL",
        "CMS",
        "EXPRESS AT",
        "EXPRESS AM",
        "GSAT",
        "HORIZONS",
        "INSAT",
        "JCSAT",
        "KAZSAT",
        "MEASAT",
        "NSS",
        "PAKSAT",
        "PSN",
        "SES",
        "TKSAT",
        "VIASAT",
        "VINASAT",
        "WILDBLUE",
        "XM ",
    ]

    if (any(substring in name_upper for substring in dash_add)) and (
        "SERIES" not in name_upper
    ):
        name_upper = name_upper.replace(" ", "-", 1)

    # CASE 4: replacing dashes with white space
    dash_remove = ["EXPRESS AMU", "THURAYA"]
    if any(substring in name_upper for substring in dash_remove):
        name_upper = name_upper.replace("-", " ", 1)

    new_name = name_upper
    return new_name


def save_dict_to_json(aws_bucket: str, dictionary: dict, filename: str):
    """
    Saves dictionary to a json file in the AWS bucket.

    Parameters
    ----------
    aws_bucket: str
        AWS bucket name
    dictionary: dict
        Dictionary to write to json
    filename: str
        String containing filename to save the json file to in the bucket
    """
    json_object = json.dumps(dictionary, indent=4)
    with open(f"s3://{aws_bucket}/{filename}.json", "w") as outfile:
        outfile.write(json_object)


def save_dict_to_pkl(aws_bucket: str, dictionary: dict, filename: str):
    """
    Saves dictionary to a pkl file in the AWS bucket.

    Parameters
    ----------
    aws_bucket: str
        AWS bucket name
    dictionary: dict
        Dictionary to write to pkl
    filename: str
        String containing filename to save the pkl file to in the bucket
    """
    with open(f"s3://{aws_bucket}/{filename}.pkl", "wb") as handle:
        pickle.dump(dictionary, handle)


def save_df_to_csv(bucket: str, client: boto3.client, df: pd.DataFrame, filename: str):
    """
    Saves dataframe to a csv file in the AWS bucket.

    Parameters
    ----------
    aws_bucket: str
        AWS bucket name
    df: pd.DataFrame
        Dataframe to write to csv
    filename: str
        String containing filename to save the csv file to in the bucket
    """
    # Save the DataFrame to a CSV file

    client.put_object(Bucket=bucket,Key=filename,Body= df.to_csv(index=False))
    


# def save_footprints(
#     aws_client: botocore.client, aws_bucket: str, sat_names: list, footprints: list
# ):
#     """
#     Saves satbeams footprints to the AWS bucket.

#     Runs threads to download images before saving to bucket.

#     Parameters
#     ----------
#     aws_client: botocore.client
#         AWS boto3 client object
#     aws_bucket: str
#         AWS bucket name
#     sat_names: list
#         List of satellite names
#     footprints: list
#         List of footprint image hrefs
#     """
#     image_encoding_dict = {}

#     images, titles = footprints[1][0], footprints[1][1]

#     q_image_encod = queue.Queue()
#     q_image_title = queue.Queue()
#     jobs = []

#     for k, sat in enumerate(sat_names):
#         thread = threading.Thread(
#             target=image_download,
#             args=(sat, images, titles, k, q_image_encod, q_image_title),
#         )
#         jobs.append(thread)

#     for j in jobs:
#         threads = threading.active_count()
#         while threads > 4:
#             time.sleep(5)
#             threads = threading.active_count()
#         j.start()
#         encodings = q_image_encod.get()
#         encod_titles = q_image_title.get()
#         for i in range(len(encodings)):
#             image_encoding_dict[encod_titles[i]] = encodings[i]
#     for j in jobs:
#         j.join()

#     pickle_byte_obj = pickle.dumps(image_encoding_dict)
#     # / causes problem with directory name
#     if "/" in key:
#         key = key.replace("/", "-")
#     key_final = f"{key}/{key}.pkl"
#     filename = f"footprints/{key_final}"
#     aws_client.put_object(Bucket=aws_bucket, Key=filename,
#                             Body=pickle_byte_obj)



# def image_download(
#     sat_name: str,
#     image_links: list,
#     image_titles: list,
#     iter_: int,
#     queue_for_image_encodings: queue.Queue,
#     queue_for_image_titles: queue.Queue,
# ):
#     """
#     Download footprint images.

#     Parameters
#     ----------
#     sat_name: str
#         String containing satellite name
#     image_links: list
#         List of footprint image hrefs
#     image_titles: list
#         List of footprint image titles
#     iter_: int
#         Iterator to keep track of list elements needed for a given satellite
#     queue_for_image_encodings: queue.Queue
#         Queue to put satellite footprint image encodings onto.
#     queue_for_image_titles: queue.Queue
#         Queue to put satellite footprint image titles onto.
#     """
#     encodings = []
#     titles = []
#     try:
#         sat_images = image_links[iter_]
#         sat_titles = image_titles[iter_]
#         # download and save images
#         print("Downloading images for", sat_images)
#         for i, image in tqdm(enumerate(sat_images)):
#             try:
#                 jpg_name = f"{sat_titles[i]}.jpg"
#             except:
#                 print("Unable to download image")

#             try:
#                 response = requests.get(image, stream=True)  # Heroku has specified timeout
#                 if response.status_code == HTTP_SUCCESS:
#                     response.raw.decode_content = True
#                     in_mem_file = BytesIO()
#                     shutil.copyfileobj(response.raw, in_mem_file)
#                     response.close()
#                     in_mem_file.seek(0)
#                     # create image encoding
#                     img = Image.open(in_mem_file)
#                     # add encoding to dict
#                     encodings.append(img)
#                     titles.append(f"{sat_name}/{sat_titles[i]}")
#                     print("Image download successful")
#             except:
#                 print("Unable to download image", sat_name, jpg_name)
#         queue_for_image_encodings.put(encodings)
#         queue_for_image_titles.put(titles)
#     except:
#         print("Unable to download images")
#         pass


def save_tables(aws_client: botocore.client, aws_bucket: str, dict_: dict):
    """
    Saves lyngsat channels tables to the AWS bucket.

    Parameters
    ----------
    aws_bucket: str
        AWS bucket name
    dict_: dict
        Dictionary of channels tables
    """
    for key, val in dict_.items():
        # / causes problem with directory name
        if "/" in key:
            key = key.replace("/", "-")
        key_final = f"{key}/{key}.csv"
        filename = f"channels/{key_final}"
        aws_client.put_object(Bucket=aws_bucket, Key=filename,Body= val.to_csv(index=False))


def save_pdfs(aws_client: botocore.client, aws_bucket: str, names: list, urls: list):
    """
    Saves altervista frequency plans to the AWS bucket.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    names: list
        List of satellite names
    urls: list
        List of satellite frequency plan urls
    Returns
    """
    # for i, url in enumerate(urls):
    #     sat_name = names[i]
    #     file_path = f"data/freq_plans/{sat_name}/"
    #     try:
    #         req = requests.get(url)
    #         req.close()
    #         pdf_name = f"{sat_name}.pdf"
    #         # write pdf to s3 bucket
    #         aws_client.put_object(
    #             Body=req.content, Bucket=aws_bucket, Key=file_path + pdf_name
    #         )
    #         # read pdf from s3 bucket
    #         obj = aws_client.get_object(Bucket=aws_bucket, Key=file_path + pdf_name)[
    #             "Body"
    #         ].read()
    #         pdf = pdfium.PdfDocument(BytesIO(obj))

    #         n_pages = len(pdf)
    #         # save pdf as new jpg
    #         for i in range(n_pages):
    #             jpg_name = f"{sat_name}_{str(i)}.jpg"
    #             page = pdf[i]
    #             in_mem_file = BytesIO()
    #             pil_image = page.render().to_pil()
    #             pil_image.save(in_mem_file, format="JPEG")
    #             in_mem_file.seek(0)
    #             aws_client.put_object(
    #                 Body=in_mem_file, Bucket=aws_bucket, Key=file_path + jpg_name
    #             )

    #         print("File", sat_name, "downloaded successfully")
    #     except:
    #         print("File", sat_name, "unable to download")
