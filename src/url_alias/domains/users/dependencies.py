from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.database import get_session
from url_alias.domains.users.models import User
from url_alias.domains.users.services import UserService
from url_alias.shared.logging import get_logger

security = HTTPBasic()
logger = get_logger(__name__)


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session=session)


async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Dependency to get the current authenticated user via Basic Auth.
    Raises HTTPException 401 if credentials are invalid or user not found.
    """
    logger.debug(f"Basic auth attempt for user: {credentials.username}")

    user = await user_service.authenticate_user(username=credentials.username, password=credentials.password)

    if not user:
        logger.warning(f"Basic auth failed for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not user.is_active:
        logger.warning(f"User {credentials.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info(f"Successfully authenticated user: {user.username}")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (alias for backward compatibility)
    """
    return current_user
