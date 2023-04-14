from fastapi import FastAPI

from .routers.urls import router as urls_router
from .routers.statistics import router as statistics_router

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener API built with FastAPI.",
    version="1.0.0",
)

app.include_router(urls_router)
app.include_router(statistics_router)
