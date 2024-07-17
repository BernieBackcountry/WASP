"""
This module defines functions for navigating and creating directories,
encoding images, and checking file status and retreiving file keys from the AWS bucket.

FUNCTIONS
    def get_project_path() -> Path:
        Return a new path object representing the current directory.
    def encode_image(path: Path) -> html.Img:
        Encodes image and returns decoded html image object.
    def prefix_exists(
        aws_client: botocore.client,
        aws_bucket: str,
        key: str
    ) -> bool:
        Checks if a given prefix exists in the AWS bucket.
    def get_file_keys(
        aws_client: botocore.client,
        aws_bucket: str,
        prefix: str,
        file_extension: str
    ) -> list:
        Retrieve item paths of a given prefix and file type from the AWS bucket.
"""

import base64
from pathlib import Path

import botocore
import boto3
from dash import html
from flask import request


def get_project_path() -> Path:
    """
    Return a new path object representing the current directory.

    Returns
    -------
    Path
        Concrete path for the current directory
    """
    return Path.cwd()


def encode_image(path: Path) -> html.Img:
    """
    Encodes image and returns decoded html image object.

    Parameters
    ----------
    path: Path
        Concrete path for the image

    Returns
    -------
    html.Img
        html image object
    """
    with open(path, "rb") as file:
        encoded_image = base64.b64encode(file.read())
    return html.Img(
        src="data:image/png;base64,{}".format(encoded_image.decode()), height="49%"
    )


def prefix_exists(aws_client: botocore.client, aws_bucket: str, key: str) -> bool:
    """
    Checks if a given prefix exists in the AWS bucket.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    key: str
        String containing prefix to check

    Returns
    -------
    bool
        True if prefix exists
        False otherwise
    """
    try:
        aws_client.head_object(Bucket=aws_bucket, Key=key)
        return True
    except:  # pylint: disable=bare-except
        return False


def get_file_keys(
    aws_client: botocore.client, aws_bucket: str, prefix: str, file_extension: str
) -> list:
    """
    Retrieve item paths of given prefix and file type from the AWS bucket.

    Parameters
    ----------
    aws_client: botocore.client
        AWS boto3 client object
    aws_bucket: str
        AWS bucket name
    key: str
        String indicating prefix of interest
    file_extension: str
        String indicating file type of interest
    Returns
    -------
    file_keys:
        List of item locations in the AWS bucket
    """
    file_keys = []
    # Create a reusable Paginator
    paginator = aws_client.get_paginator("list_objects_v2")
    # Create a PageIterator from the Paginator with prefix items
    page_iterator = paginator.paginate(Bucket=aws_bucket, Prefix=prefix)
    # iterate through items and get select file keys
    for page in page_iterator:
        if "Contents" in page:
            for key in page["Contents"]:
                key_string = key["Key"]
                if file_extension in key_string:
                    file_keys.append(key_string)
    return file_keys
