import boto3
import os
import time
import wasp_tool.utilities as utilities


AWS_CLIENT = boto3.client(
    's3',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'))

AWS_BUCKET_NAME = 'bucketeer-a740be18-be27-4fe6-923e-d10c734ba19c'

start_time = time.time()

# Scrap Altervista data
altervista_data, altervista_pdfs = utilities.prepare_altervista('http://frequencyplansatellites.altervista.org/')
utilities.save_dict_to_csv(AWS_BUCKET_NAME, altervista_data, "altervista.csv")
utilities.save_pdfs(AWS_CLIENT, AWS_BUCKET_NAME, altervista_data['priSatName'], altervista_pdfs)
print("--- %s seconds ---" % (time.time() - start_time))
print("ALTERVISTA COMPLETE") 