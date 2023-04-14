from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class CreateUrl(BaseModel):
    url: str


class ClickInfo(BaseModel):
    timestamp: datetime
    referrer: str


class UrlEntry(BaseModel):
    id: str
    url: str
    created_at: datetime
    clicks: List[ClickInfo] = []

    def dict(self, *args, **kwargs):
        url_entry_dict = super().dict(*args, **kwargs)
        url_entry_dict["created_at"] = url_entry_dict["created_at"].isoformat()
        for click in url_entry_dict["clicks"]:
            click["timestamp"] = click["timestamp"].isoformat()
        return url_entry_dict


class StatisticSummary(BaseModel):
    total_clicks: int
    clicks_per_day: Dict[str, int]
    referrers: Dict[str, int]
