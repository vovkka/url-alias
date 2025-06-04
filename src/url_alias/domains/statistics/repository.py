from datetime import datetime
from typing import Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.repository import BaseRepository
from url_alias.db.schema import AppBaseSchema
from url_alias.domains.aliases.models import Alias
from url_alias.domains.statistics.models import AliasStatistic


class StatisticRepoCreate(AppBaseSchema):
    alias_id: int
    total_clicks: int = 0
    last_hour_clicks: int = 0
    last_day_clicks: int = 0
    last_hour_updated_at: Optional[datetime] = None
    last_day_updated_at: Optional[datetime] = None
    last_clicked_at: Optional[datetime] = None


class StatisticRepoUpdate(AppBaseSchema):
    total_clicks: Optional[int] = None
    last_hour_clicks: Optional[int] = None
    last_day_clicks: Optional[int] = None
    last_hour_updated_at: Optional[datetime] = None
    last_day_updated_at: Optional[datetime] = None
    last_clicked_at: Optional[datetime] = None


class StatisticRepository(BaseRepository[AliasStatistic, StatisticRepoCreate, StatisticRepoUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=AliasStatistic, session=session)

    async def get_by_alias_id(self, alias_id: int) -> Optional[AliasStatistic]:
        """Get statistics for a specific alias."""
        statement = select(self.model).where(self.model.alias_id == alias_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_statistics_summary(self, user_id: int, sort_order: str = "desc", limit: int = 100, offset: int = 0):
        """Get aggregated statistics for user's aliases with pagination."""
        order_func = desc if sort_order == "desc" else asc

        statement = (
            select(
                Alias.short_code,
                Alias.target_url,
                AliasStatistic.total_clicks,
                AliasStatistic.last_hour_clicks,
                AliasStatistic.last_day_clicks,
            )
            .select_from(Alias)
            .outerjoin(AliasStatistic, Alias.id == AliasStatistic.alias_id)
            .where(Alias.short_code.isnot(None), Alias.user_id == user_id)
            .order_by(order_func(AliasStatistic.total_clicks))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(statement)
        return result.all()
