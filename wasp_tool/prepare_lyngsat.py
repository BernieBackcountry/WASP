import wasp_tool.utilities as utilities
import time
import os
import boto3


# get AWS s3 bucket
AWS_CLIENT = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'))

AWS_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME') 

start_time = time.time()

# Scrap Lyngsat data
lyngsat_data, lyngsat_tables = utilities.prepare_lyngsat('https://www.lyngsat.com/')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, lyngsat_data, "lyngsat.csv")
utilities.save_tables(AWS_BUCKET_NAME, lyngsat_tables)
print("--- %s seconds ---" % (time.time() - start_time))
print("LYNGSAT COMPLETE")