"""
This module pulls and prepares data from the specified site(s) of interest. The
data is written to the AWS bucket.
"""
import argparse
import os
import sys
import time
import boto3
from wasp_tool import utilities
import pandas as pd
from config import KEY,SECRET_KEY,BUCKET_NAME
import numpy as np
import warnings

#warnings.simplefilter("ignore")


session = boto3.session.Session()

DIGITAL_OCEAN_CLIENT = session.client(
    's3',
    region_name='nyc3',
    endpoint_url="https://newsatbucket.nyc3.digitaloceanspaces.com",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET_KEY,
)


def create_s3_bucket(client):
    """
    Creates an Amazon S3 bucket.

    :param bucket_name: The unique name for your bucket.
    """
    
    try:
        client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created successfully!")
    except Exception as e:
        print(f"Error creating bucket: {e}")


def measure_time(f):
    """
    Measure and print runtime for all functions.

    Parameters
    ----------
    f
        Function to measure.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        print(
            "{:s} function took {:.3f} mins".format(
                f.__name__, (start_time - end_time) / 60
            )
        )
        return result

    return wrapper


@measure_time
def get_altervista_data():
    """
    Retrieve data obtained from frequencyplansatellites.altervista.org and write
    to the AWS bucket
    """
    altervista_data = utilities.prepare_altervista()
    utilities.save_df_to_csv(
        BUCKET_NAME, DIGITAL_OCEAN_CLIENT, altervista_data, "altervista.csv")
    utilities.save_pdfs(DIGITAL_OCEAN_CLIENT, BUCKET_NAME,
                        altervista_data["Primary Satellite"].to_list(), altervista_data)


@measure_time
def get_celestrak_data():
    """
    Retrieve data obtained from celestrak.com and write to the AWS bucket
    """
    celestrak_data = utilities.prepare_celestrak()

    """
    Turn dict into df by indexing then flattening
    """
    celestrak_data.to_csv("celestrak.csv", index=False)
    utilities.save_df_to_csv(
        BUCKET_NAME, DIGITAL_OCEAN_CLIENT, celestrak_data, "celestrak.csv")


@measure_time
def get_lyngsat_data():
    """
    Retrieve data obtained from lyngsat.com and write to the AWS bucket
    """
    utilities.prepare_lyngsat()
    lyngsat_data, lyngsat_tables = utilities.prepare_lyngsat()
    lyngsat_data_df = pd.DataFrame(lyngsat_data)
    utilities.save_df_to_csv(
        BUCKET_NAME, DIGITAL_OCEAN_CLIENT, lyngsat_data_df, "lyngsat.csv")
    utilities.save_tables(DIGITAL_OCEAN_CLIENT,BUCKET_NAME, lyngsat_tables)


@measure_time
def get_satbeams_data():
    """
    Retrieve data obtained from satbeams.org and write to the AWS bucket
    """
    satbeams_data, satbeams_footprints = utilities.prepare_satbeams()
    utilities.save_df_to_csv(
        BUCKET_NAME, DIGITAL_OCEAN_CLIENT, satbeams_data, "satbeams.csv")

    utilities.save_footprints(
        DIGITAL_OCEAN_CLIENT, BUCKET_NAME, satbeams_data["Primary Satellite"].tolist(), satbeams_footprints)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site",
        nargs="+",
        help="Options: altervista, celestrak, lyngsat, satbeams and/or all",
        required=True,
    )


    parser_args = parser.parse_args()

    if "all" in parser_args.site:
        get_altervista_data()
        get_celestrak_data()
        get_lyngsat_data()
        get_satbeams_data()
        sys.exit()
    if "altervista" in parser_args.site:
        get_altervista_data()
    if "celestrak" in parser_args.site:
        get_celestrak_data()
    if "lyngsat" in parser_args.site:
        get_lyngsat_data()
    if "satbeams" in parser_args.site:
        get_satbeams_data()
    # if "data" in parser_args.site:
    #     get_blank_data()

    
