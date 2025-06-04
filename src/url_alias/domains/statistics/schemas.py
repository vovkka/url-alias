from enum import Enum

from pydantic import Field

from url_alias.db.schema import AppBaseSchema


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class StatisticSummary(AppBaseSchema):
    short_url: str = Field(..., description="Full short URL (e.g., http://localhost:8000/abc123)")
    target_url: str = Field(..., description="Original target URL")
    last_hour_clicks: int = Field(..., description="Number of clicks in the last hour")
    last_day_clicks: int = Field(..., description="Number of clicks in the last day")
    total_clicks: int = Field(..., description="Total number of clicks")
