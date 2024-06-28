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


os.environ["secret_key"] = "5av74jgXu9/JTAlM6QT71heoLU2X26C3q8wN57j8i90"
os.environ["key"] = "DO009ERY4P8RHV3DZMYQ"
DIGITAL_OCEAN_BUCKET = "newsatbucket" 
session = boto3.session.Session()

DIGITAL_OCEAN_CLIENT = session.client(
    's3',
    region_name='nyc3',
    endpoint_url="https://newsatbucket.nyc3.digitaloceanspaces.com",
    aws_access_key_id=os.getenv("key"),
    aws_secret_access_key=os.getenv("secret_key"),
)

def create_s3_bucket(bucket_name,client):
    """
    Creates an Amazon S3 bucket.

    :param bucket_name: The unique name for your bucket.
    """
    
    try:
        client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully!")
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
    altervista_data, altervista_pdfs = utilities.prepare_altervista()
    utilities.save_df_to_csv(DIGITAL_OCEAN_BUCKET, altervista_data, "altervista.csv")
    utilities.save_pdfs(DIGITAL_OCEAN_CLIENT, DIGITAL_OCEAN_BUCKET, altervista_data["priSatName"], altervista_pdfs)


@measure_time
def get_celestrak_data():
    """
    Retrieve data obtained from celestrak.com and write to the AWS bucket
    """
    celestrak_data = utilities.prepare_celestrak()

    """
    Turn dict into df by indexing then flattening
    """
    names = ['x', 'y', 'z']
    index = pd.MultiIndex.from_product(
    [range(s) for s in celestrak_data.shape], names=names)
    celestrak_data_df = pd.DataFrame({'A': celestrak_data.flatten()}, index=index)['A']

    print(celestrak_data_df)
    utilities.save_df_to_csv(DIGITAL_OCEAN_BUCKET,DIGITAL_OCEAN_CLIENT, celestrak_data_df, "celestrak.csv")


@measure_time
def get_lyngsat_data():
    """
    Retrieve data obtained from lyngsat.com and write to the AWS bucket
    """
    utilities.prepare_lyngsat()
    lyngsat_data, lyngsat_tables = utilities.prepare_lyngsat()
    utilities.save_df_to_csv(DIGITAL_OCEAN_BUCKET, lyngsat_data, "lyngsat.csv")
    utilities.save_tables(DIGITAL_OCEAN_BUCKET, lyngsat_tables)


@measure_time
def get_satbeams_data():
    """
    Retrieve data obtained from satbeams.org and write to the AWS bucket
    """
    satbeams_data, satbeams_footprints = utilities.prepare_satbeams()
    utilities.save_df_to_csv(
        DIGITAL_OCEAN_BUCKET, satbeams_data, "satbeams.csv")
    print("Saved csv")
    utilities.save_footprints(
        DIGITAL_OCEAN_CLIENT, DIGITAL_OCEAN_BUCKET, satbeams_data["priSatName"], satbeams_footprints
    )


# def get_blank_data():
#      """
#     Retrieve data obtained from empty df
#     """
#      data = pd.DataFrame(columns = ["Did", "This", "Work"])
#      utilities.save_df_to_csv(DIGITAL_OCEAN_BUCKET,DIGITAL_OCEAN_CLIENT, data, "data.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site",
        nargs="+",
        help="Options: altervista, celestrak, lyngsat, satbeams and/or all",
        required=True,
    )

    try: 
        DIGITAL_OCEAN_CLIENT.head_bucket(Bucket=DIGITAL_OCEAN_BUCKET)
    except Exception as e:
        create_s3_bucket(DIGITAL_OCEAN_BUCKET,DIGITAL_OCEAN_CLIENT)
        print("bucket created")

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

    
