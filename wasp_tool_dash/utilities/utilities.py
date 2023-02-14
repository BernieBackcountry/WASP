import base64
from dash import html
from pathlib import Path
import botocore


def get_project_path() -> Path:
    return Path.cwd()


def encode_image(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='49%')


def encode_image_pdf(path: Path) -> html.Img:
    encoded_image = base64.b64encode(open(path, 'rb').read())
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width='90%')


def prefix_exists(aws_client: botocore.client, aws_bucket: str, key: str):
    try:
        aws_client.head_object(Bucket=aws_bucket, Key=key)
        return True
    except:
        return False


def get_file_keys(aws_client: botocore.client, aws_bucket: str, prefix: str, file_extension: str):
    file_keys = []
    paginator = aws_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=aws_bucket, Prefix=prefix)
    for page in page_iterator:
        if "Contents" in page:  
            for key in page["Contents"]:
                keyString = key["Key"]
                if file_extension in keyString:
                    file_keys.append(keyString)
    return file_keys
