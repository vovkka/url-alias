from fastapi import APIRouter, Depends, HTTPException, Request, status

from url_alias.domains.users.dependencies import get_current_active_user, get_user_service
from url_alias.domains.users.models import User as UserModel
from url_alias.domains.users.schemas import UserCreate, UserRead
from url_alias.domains.users.services import UserService
from url_alias.shared.logging import get_logger
from url_alias.shared.rate_limiting import limiter

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

logger = get_logger(__name__)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register_user(
    request: Request, user_create: UserCreate, user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user. Public endpoint.
    Rate limited to 5 registrations per hour per IP.
    """
    logger.info(f"Registration attempt for username: {user_create.username}")

    try:
        existing_user = await user_service.user_repository.get_by_username(user_create.username)
        if existing_user:
            logger.warning(f"Registration failed: username {user_create.username} already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        created_user = await user_service.create_user(user_in=user_create)
        logger.info(f"Successfully registered user: {created_user.username}")
        return UserRead.model_validate(created_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user {user_create.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the user.",
        )


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get current user information. Requires Basic Auth.
    """
    logger.info(f"Fetching info for user: {current_user.username}")
    return UserRead.model_validate(current_user)
