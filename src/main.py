import json
import os
import string
from pathlib import Path
from secrets import choice
from typing import List

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from mangum import Mangum
from pydantic import BaseModel, parse_obj_as

ENV = os.environ.get("APP_ENV", "dev")

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener API built with FastAPI.",
    version="1.0.0",
)

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


class UrlEntry(BaseModel):
    id: str
    url: str


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


@app.post("/urls", response_model=UrlEntry, status_code=status.HTTP_201_CREATED)
async def create_url(url: str):
    """
    Create a new shortened URL for the given `url`.

    If the `url` has already been shortened, returns the existing shortened URL.
    """
    data = read_data()

    for entry in data:
        if entry.url == url:
            return entry

    new_id = generate_id()
    while any(entry.id == new_id for entry in data):
        new_id = generate_id()

    new_entry = UrlEntry(id=new_id, url=url)
    data.append(new_entry)
    write_data(data)

    return new_entry


@app.get("/urls", response_model=List[UrlEntry])
async def list_urls():
    """
    Get a list of all shortened URLs stored in the system.

    Returns a list of `UrlEntry` objects containing the `id` and `url` for each shortened URL.
    """
    return read_data()


@app.get("/urls/{id}", response_model=UrlEntry)
async def get_url(id: str):
    """
    Get a shortened URL by its `id`.

    If the `id` is not found, returns a 404 error with a detail message.
    """
    data = read_data()
    for entry in data:
        if entry.id == id:
            return entry
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@app.get(
    "/{id}",
    summary="Redirect to full URL",
    response_description="A redirection to the full URL",
)
async def redirect_url(id: str):
    """
    Redirect the user to the full URL associated with the given short URL ID.

    If the `id` is not found, returns a 404 error with a detail message.
    """
    data = read_data()
    url_entry = next((entry for entry in data if entry.id == id), None)

    if url_entry:
        return RedirectResponse(
            url=url_entry.url, status_code=status.HTTP_301_MOVED_PERMANENTLY
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ID not found"
        )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if ENV == "prod":
    handler = Mangum(app=app)
