from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.domains.users.models import User
from url_alias.domains.users.repository import UserRepoCreate, UserRepository
from url_alias.domains.users.schemas import UserCreate
from url_alias.domains.users.security import get_password_hash, verify_password
from url_alias.shared.logging import get_service_logger


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session=session)
        self.logger = get_service_logger("users")

    async def create_user(self, *, user_in: UserCreate) -> User:
        """Creates a new user, hashes the password, and saves to the database."""
        self.logger.info(f"Creating new user with username: {user_in.username}")

        try:
            hashed_password = get_password_hash(user_in.password)
            repo_create_data = UserRepoCreate(
                username=user_in.username,
                hashed_password=hashed_password,
            )
            created_user = await self.user_repository.create(obj_in=repo_create_data)

            self.logger.info(f"Successfully created user with ID: {created_user.id}, username: {created_user.username}")
            return created_user

        except Exception as e:
            self.logger.error(f"Failed to create user {user_in.username}: {str(e)}")
            raise

    async def authenticate_user(self, *, username: str, password: str) -> Optional[User]:
        """Authenticates a user by username and password."""
        self.logger.debug(f"Attempting to authenticate user: {username}")

        try:
            user = await self.user_repository.get_by_username(username=username)
            if not user:
                self.logger.warning(f"Authentication failed: user {username} not found")
                return None
            if not user.is_active:
                self.logger.warning(f"Authentication failed: user {username} is inactive")
                return None
            if not verify_password(plain_password=password, hashed_password=user.hashed_password):
                self.logger.warning(f"Authentication failed: invalid password for user {username}")
                return None

            self.logger.info(f"Successfully authenticated user: {username}")
            return user

        except Exception as e:
            self.logger.error(f"Error during authentication for user {username}: {str(e)}")
            raise

    async def get_all_users(self) -> List[User]:
        """Get all users from the database."""
        self.logger.info("Fetching all users from database")

        try:
            users = await self.user_repository.get_all()
            self.logger.info(f"Successfully fetched {len(users)} users")
            return users

        except Exception as e:
            self.logger.error(f"Failed to fetch users: {str(e)}")
            raise
