import os
import time

import boto3

import wasp_tool.utilities as utilities


# get AWS s3 bucket
AWS_CLIENT = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'))

AWS_BUCKET_NAME = 'bucketeer-40b6657d-c39a-4bb2-b827-f1fe40ec93db' #os.environ.get('S3_BUCKET_NAME') 

start_time = time.time()

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, celestrak_data, "celestrak.csv")
print("--- %s seconds ---" % (time.time() - start_time))
print("CELESTRAK COMPLETE")

# Scrap Lyngsat data
lyngsat_data, lyngsat_tables = utilities.prepare_lyngsat('https://www.lyngsat.com/')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, lyngsat_data, "lyngsat.csv")
utilities.save_tables(AWS_BUCKET_NAME, lyngsat_tables)
print("--- %s seconds ---" % (time.time() - start_time))
print("LYNGSAT COMPLETE")

# Scrap Altervista data
altervista_data, altervista_pdfs = utilities.prepare_altervista('http://frequencyplansatellites.altervista.org/')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, altervista_data, "altervista.csv")
utilities.save_pdfs(AWS_CLIENT, AWS_BUCKET_NAME, altervista_data['priSatName'], altervista_pdfs)
print("--- %s seconds ---" % (time.time() - start_time))
print("ALTERVISTA COMPLETE") 

# Scrap Satbeams data
satbeams_data, satbeams_footprints = utilities.prepare_satbeams('https://satbeams.com/satellites?status=active')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, satbeams_data, "satbeams.csv")
utilities.save_footprints(AWS_CLIENT, AWS_BUCKET_NAME, satbeams_data["priSatName"], satbeams_footprints)
print("--- %s seconds ---" % (time.time() - start_time))
print("SATBEAMS COMPLETE")


