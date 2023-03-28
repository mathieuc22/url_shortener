import json
import random
import string
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener API built with FastAPI.",
    version="1.0.0",
)

data_file = "urls.json"


class UrlEntry(BaseModel):
    id: str
    url: str


def read_data():
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
        return [UrlEntry(**entry) for entry in data]
    except FileNotFoundError:
        return []


def write_data(data: List[UrlEntry]):
    with open(data_file, "w") as f:
        data_as_dicts = [entry.dict() for entry in data]
        json_data = json.dumps(data_as_dicts, indent=2)
        f.write(json_data)


def generate_id(size=5):
    return "".join(random.choices(string.ascii_letters + string.digits, k=size))


@app.post("/urls", response_model=UrlEntry)
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
    raise HTTPException(status_code=404, detail="URL not found")


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
