import boto3
import os
import wasp_tool.utilities as utilities


AWS_CLIENT = boto3.client(
    's3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'))

AWS_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME') 

# Scrap Celestrak data
celestrak_data = utilities.prepare_celestrak('https://celestrak.com/NORAD/elements/geo.txt')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, celestrak_data, "celestrak.csv")
print("CELESTRAK COMPLETE")