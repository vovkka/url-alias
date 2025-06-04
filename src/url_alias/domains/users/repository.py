from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.repository import BaseRepository
from url_alias.db.schema import AppBaseSchema
from url_alias.domains.users.models import User


class UserRepoInput(AppBaseSchema):
    username: str
    is_active: Optional[bool] = None


class UserRepoCreate(UserRepoInput):
    hashed_password: str
    is_active: bool = True


class UserRepoUpdate(AppBaseSchema):
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRepository(BaseRepository[User, UserRepoCreate, UserRepoUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        statement = select(self.model).where(self.model.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
