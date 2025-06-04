from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.repository import BaseRepository
from url_alias.db.schema import AppBaseSchema
from url_alias.domains.aliases.models import Alias


class AliasRepoInput(AppBaseSchema):
    target_url: str
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = None
    is_enabled: bool = True


class AliasRepoCreate(AliasRepoInput):
    pass


class AliasRepoUpdate(AliasRepoInput):
    target_url: Optional[str] = None
    is_enabled: Optional[bool] = None
    short_code: Optional[str] = None


class AliasRepository(BaseRepository[Alias, AliasRepoCreate, AliasRepoUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Alias, session=session)

    async def get_by_short_code(self, short_code: str) -> Optional[Alias]:
        """Get an alias by its short code."""
        statement = select(self.model).where(self.model.short_code == short_code)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all_by_target_url(self, target_url: str) -> List[Alias]:
        """Get all aliases matching a target URL."""
        statement = select(self.model).where(self.model.target_url == target_url)
        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_user_aliases(
        self, user_id: int, active_only: bool = False, limit: int = 100, offset: int = 0
    ) -> List[Alias]:
        """Get aliases for a specific user with pagination."""
        statement = select(self.model).where(self.model.user_id == user_id)

        if active_only:
            now = datetime.now(timezone.utc)
            statement = statement.where(
                self.model.is_enabled == True,  # noqa: E712
                (self.model.expires_at.is_(None)) | (self.model.expires_at > now),
            )

        statement = statement.order_by(self.model.created_at.desc()).limit(limit).offset(offset)

        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_by_id_and_user(self, alias_id: int, user_id: int) -> Optional[Alias]:
        """Get an alias by ID if it belongs to the specified user."""
        statement = select(self.model).where(self.model.id == alias_id, self.model.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_short_code_and_user(self, short_code: str, user_id: int) -> Optional[Alias]:
        """Get an alias by short code if it belongs to the specified user."""
        statement = select(self.model).where(self.model.short_code == short_code, self.model.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
