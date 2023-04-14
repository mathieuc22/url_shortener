import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

from src.api import app as api_app

ENV = os.environ.get("APP_ENV", "dev")

origins = [
    "http://localhost:5173",
    "https://lienb.fr",
]


def custom_openapi():
    if api_app.openapi_schema:
        return api_app.openapi_schema

    openapi_schema = get_openapi(
        title=api_app.title,
        version=api_app.version,
        description=api_app.description,
        routes=api_app.routes,
    )

    api_app.openapi_schema = openapi_schema
    return api_app.openapi_schema


api_app.openapi = custom_openapi


api_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if ENV == "prod":
    handler = Mangum(app=api_app)
