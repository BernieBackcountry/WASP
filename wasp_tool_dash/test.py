import os
import boto3
import dash
import pandas as pd
from dash.dependencies import Input, Output

from wasp_tool_dash import utilities
from wasp_tool_dash.utilities import populate_utilities
from wasp_tool_dash.components import LayoutCreator
from wasp_tool.prepare import get_celestrak_data
from config import BUCKET_NAME, KEY, SECRET_KEY

session = boto3.session.Session()

session = boto3.session.Session()

AWS_CLIENT = session.client(
    's3',
    region_name='nyc3',
    endpoint_url="https://newsatbucket.nyc3.digitaloceanspaces.com",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET_KEY,
)

AWS_BUCKET_NAME = BUCKET_NAME

PATH_KEY = "newsatbucket/"


response = AWS_CLIENT.head_object(Bucket=AWS_BUCKET_NAME, Key="celestrak.csv")

print(response)


