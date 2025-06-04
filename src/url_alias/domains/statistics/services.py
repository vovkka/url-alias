from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.domains.statistics.repository import StatisticRepoCreate, StatisticRepository, StatisticRepoUpdate
from url_alias.domains.statistics.schemas import StatisticSummary
from url_alias.shared.logging import get_service_logger


class StatisticService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.statistic_repository = StatisticRepository(session=session)
        self.logger = get_service_logger("statistics")

    async def record_click(self, alias_id: int) -> None:
        """Record a click for an alias with business logic."""
        self.logger.info(f"Recording click for alias ID: {alias_id}")

        try:
            now = datetime.now(timezone.utc)

            existing_statistic = await self.statistic_repository.get_by_alias_id(alias_id)

            if existing_statistic:
                await self._update_existing_statistic(existing_statistic, now)
                self.logger.debug(f"Updated existing statistic for alias {alias_id}")
            else:
                await self._create_new_statistic(alias_id, now)
                self.logger.debug(f"Created new statistic for alias {alias_id}")

        except Exception as e:
            self.logger.error(f"Failed to record click for alias {alias_id}: {str(e)}")
            raise

    async def get_statistics_summary(
        self, user_id: int, base_url: str, sort_order: str = "desc", limit: int = 100, offset: int = 0
    ) -> List[StatisticSummary]:
        """Get aggregated statistics for user's aliases with pagination."""
        self.logger.info(
            f"Fetching statistics summary for user {user_id} "
            f"with sort_order: {sort_order}, limit: {limit}, offset: {offset}"
        )

        try:
            raw_stats = await self.statistic_repository.get_statistics_summary(user_id, sort_order, limit, offset)

            statistics = []
            for row in raw_stats:
                short_url = f"{base_url}/{row.short_code}"
                statistics.append(
                    StatisticSummary(
                        short_url=short_url,
                        target_url=row.target_url,
                        last_hour_clicks=row.last_hour_clicks or 0,
                        last_day_clicks=row.last_day_clicks or 0,
                        total_clicks=row.total_clicks or 0,
                    )
                )

            self.logger.info(f"Successfully fetched {len(statistics)} statistics records for user {user_id}")
            return statistics

        except Exception as e:
            self.logger.error(f"Failed to fetch statistics summary for user {user_id}: {str(e)}")
            raise

    async def _update_existing_statistic(self, statistic, now: datetime) -> None:
        """Update existing statistic record with new click."""
        updates = {"total_clicks": statistic.total_clicks + 1, "last_clicked_at": now}

        if self._should_reset_hour_counter(statistic.last_hour_updated_at, now):
            updates["last_hour_clicks"] = 1
            updates["last_hour_updated_at"] = now
        else:
            updates["last_hour_clicks"] = statistic.last_hour_clicks + 1

        if self._should_reset_day_counter(statistic.last_day_updated_at, now):
            updates["last_day_clicks"] = 1
            updates["last_day_updated_at"] = now
        else:
            updates["last_day_clicks"] = statistic.last_day_clicks + 1

        update_data = StatisticRepoUpdate(**updates)
        await self.statistic_repository.update(db_obj=statistic, obj_in=update_data)

    async def _create_new_statistic(self, alias_id: int, now: datetime) -> None:
        """Create new statistic record for first click."""
        create_data = StatisticRepoCreate(
            alias_id=alias_id,
            total_clicks=1,
            last_hour_clicks=1,
            last_day_clicks=1,
            last_hour_updated_at=now,
            last_day_updated_at=now,
            last_clicked_at=now,
        )
        await self.statistic_repository.create(obj_in=create_data)

    def _should_reset_hour_counter(self, last_updated, now: datetime) -> bool:
        """Check if hour counter should be reset."""
        if not last_updated:
            return False
        return now - last_updated >= timedelta(hours=1)

    def _should_reset_day_counter(self, last_updated, now: datetime) -> bool:
        """Check if day counter should be reset."""
        if not last_updated:
            return False
        return now - last_updated >= timedelta(days=1)
