from datetime import datetime
from typing import List

from pydantic import BaseModel


class ClickInfo(BaseModel):
    timestamp: datetime
    referrer: str


class UrlEntry(BaseModel):
    id: str
    url: str
    clicks: List[ClickInfo] = []

    def dict(self, *args, **kwargs):
        url_entry_dict = super().dict(*args, **kwargs)
        for click in url_entry_dict["clicks"]:
            click["timestamp"] = click["timestamp"].isoformat()
        return url_entry_dict
