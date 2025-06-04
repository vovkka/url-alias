from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.database import get_session
from url_alias.domains.statistics.services import StatisticService


def get_statistic_service(session: AsyncSession = Depends(get_session)) -> StatisticService:
    return StatisticService(session=session)
