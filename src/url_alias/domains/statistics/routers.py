from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from url_alias.domains.statistics.dependencies import get_statistic_service
from url_alias.domains.statistics.schemas import SortOrder, StatisticSummary
from url_alias.domains.statistics.services import StatisticService
from url_alias.domains.users.dependencies import get_current_active_user
from url_alias.domains.users.models import User as UserModel

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
)


@router.get("", response_model=List[StatisticSummary])
async def get_statistics_summary(
    request: Request,
    statistic_service: StatisticService = Depends(get_statistic_service),
    current_user: UserModel = Depends(get_current_active_user),
    sort_order: SortOrder = SortOrder.DESC,
    page: int = Query(default=1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
):
    """
    Get aggregated statistics for user's aliases sorted by total clicks with pagination.
    Requires Basic Auth.
    """
    try:
        base_url = str(request.base_url).rstrip("/")
        offset = (page - 1) * page_size

        statistics = await statistic_service.get_statistics_summary(
            user_id=current_user.id, base_url=base_url, sort_order=sort_order.value, limit=page_size, offset=offset
        )
        return statistics
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving statistics.",
        )
