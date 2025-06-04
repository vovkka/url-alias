from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.database import get_session
from url_alias.domains.aliases.services import AliasService


def get_alias_service(session: AsyncSession = Depends(get_session)) -> AliasService:
    return AliasService(session=session)
