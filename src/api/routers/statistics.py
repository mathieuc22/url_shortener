from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from ..internal.data import read_data
from ..models import UrlEntry, StatisticSummary

router = APIRouter(
    tags=["statistics"],
)


def get_url_entry(id: str) -> UrlEntry:
    data = read_data()
    url_entry = next((entry for entry in data if entry.id == id), None)
    if not url_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    return url_entry


@router.get("/statistics/{id}", response_model=StatisticSummary)
async def get_statistics(id: str, url_entry: UrlEntry = Depends(get_url_entry)):
    """
    Get statistics for the given short URL ID, including the total number of clicks, clicks per day, and referrers.
    """
    clicks = url_entry.clicks
    total_clicks = len(clicks)
    clicks_per_day = {}
    referrers = {}

    for click in clicks:
        date_str = click.timestamp.date().isoformat()
        clicks_per_day[date_str] = clicks_per_day.get(date_str, 0) + 1

        referrer = click.referrer
        referrers[referrer] = referrers.get(referrer, 0) + 1

    statistic_summary = StatisticSummary(
        total_clicks=total_clicks,
        clicks_per_day=clicks_per_day,
        referrers=referrers,
    )

    return statistic_summary
