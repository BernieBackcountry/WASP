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

secret_key = "5av74jgXu9/JTAlM6QT71heoLU2X26C3q8wN57j8i90"
key = "DO009ERY4P8RHV3DZMYQ"
DIGITAL_OCEAN_BUCKET = os.getenv("satbucket")
url = "https://satbucket.nyc3.digitaloceanspaces.com"


session = boto3.session.Session()
DIGITAL_OCEAN_CLIENT = session.client(
    's3',
    region_name='nyc3',  # Specify the correct region
    endpoint_url=url,
    aws_access_key_id=key,
    aws_secret_access_key=secret_key,
    config=boto3.session.Config(signature_version='s3v4')
)

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
    utilities.save_df_to_csv(DIGITAL_OCEAN_BUCKET, celestrak_data, "celestrak.csv")


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
