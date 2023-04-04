import json
import os
import string
from pathlib import Path
from secrets import choice
from typing import List

import boto3
from botocore.exceptions import ClientError
from pydantic import parse_obj_as

from ..models import UrlEntry

ENV = os.environ.get("APP_ENV", "dev")


FILE_NAME = "urls.json"
DATA_FILE = Path(__file__).parent.resolve() / FILE_NAME
ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

s3 = boto3.client(
    service_name="s3",
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_KEY,
)


def read_data_local():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return [UrlEntry(**entry) for entry in data]
    except FileNotFoundError:
        return []


def write_data_local(data: List[UrlEntry]):
    with open(DATA_FILE, "w") as f:
        data_as_dicts = [entry.dict() for entry in data]
        json_data = json.dumps(data_as_dicts, indent=2)
        f.write(json_data)


def read_data_s3() -> List[UrlEntry]:
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        content = response["Body"].read()
        data = json.loads(content)
        return parse_obj_as(List[UrlEntry], data)
    except ClientError as e:
        print("Error reading data from S3:", e)
        return []


def write_data_s3(data: List[UrlEntry]) -> None:
    try:
        serialized_data = json.dumps([entry.dict() for entry in data], indent=2)
        s3.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body=serialized_data)
    except ClientError as e:
        print("Error writing data to S3:", e)


def read_data() -> List[UrlEntry]:
    if ENV == "prod":
        return read_data_s3()
    else:
        return read_data_local()


def write_data(data: List[UrlEntry]) -> None:
    if ENV == "prod":
        write_data_s3(data)
    else:
        write_data_local(data)


def generate_id(size=5):
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(size))
