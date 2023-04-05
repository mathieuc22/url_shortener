from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status, Response, Body
from fastapi.responses import RedirectResponse

from ..internal.data import generate_id, read_data, write_data
from ..models import ClickInfo, UrlEntry, CreateUrl

router = APIRouter(
    tags=["urls"],
)


@router.post("/urls", response_model=UrlEntry, status_code=status.HTTP_201_CREATED)
async def create_url(
    url: Optional[str] = None,
    url_data: Optional[CreateUrl] = Body(None),
    response: Response = None,
):
    """
    Create a new shortened URL for the given `url`.

    If the `url` has already been shortened, returns the existing shortened URL.
    """
    if not url and not url_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing URL data"
        )

    if url_data:
        url = url_data.url

    data = read_data()

    for entry in data:
        if entry.url == url:
            response.status_code = status.HTTP_200_OK
            return entry

    new_id = generate_id()
    while any(entry.id == new_id for entry in data):
        new_id = generate_id()

    new_entry = UrlEntry(id=new_id, url=url, created_at=datetime.utcnow())
    data.append(new_entry)
    write_data(data)

    return new_entry


@router.get("/urls", response_model=List[UrlEntry])
async def list_urls():
    """
    Get a list of all shortened URLs stored in the system.

    Returns a list of `UrlEntry` objects containing the `id` and `url` for each shortened URL.
    """
    return read_data()


@router.get("/urls/{id}", response_model=UrlEntry)
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


@router.get(
    "/{id}",
    summary="Redirect to full URL",
    response_description="A redirection to the full URL",
)
async def redirect_url(request: Request, id: str):
    """
    Redirect the user to the full URL associated with the given short URL ID.
    If the `id` is not found, returns a 404 error with a detail message.
    """
    data = read_data()
    url_entry = next((entry for entry in data if entry.id == id), None)

    if url_entry:
        # Enregistrez les informations de clic
        referrer = request.headers.get("Referer", "unknown")
        click_info = ClickInfo(timestamp=datetime.utcnow(), referrer=referrer)
        url_entry.clicks.append(click_info)
        write_data(data)

        response = RedirectResponse(
            url_entry.url, status_code=status.HTTP_301_MOVED_PERMANENTLY
        )
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ID not found"
        )
