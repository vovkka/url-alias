from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.domains.aliases.models import Alias
from url_alias.domains.aliases.repository import AliasRepoCreate, AliasRepository, AliasRepoUpdate
from url_alias.domains.aliases.schemas import AliasCreateRequest
from url_alias.domains.aliases.utils import generate_short_code_from_id
from url_alias.shared.logging import get_service_logger


class AliasService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.alias_repository = AliasRepository(session=session)
        self.logger = get_service_logger("aliases")

    async def create_alias(self, *, alias_create_request: AliasCreateRequest, user_id: Optional[int] = None) -> Alias:
        """Orchestrates the creation of a new alias, including short_code generation."""
        self.logger.info(f"Creating new alias for URL: {alias_create_request.target_url}, user_id: {user_id}")

        try:
            repo_create_data = AliasRepoCreate(
                target_url=alias_create_request.target_url,
                expires_at=alias_create_request.expires_at,
                user_id=user_id,
                is_enabled=alias_create_request.is_enabled,
            )

            created_alias = await self.alias_repository.create(obj_in=repo_create_data)

            if created_alias.id is None:
                self.logger.error("Failed to obtain ID for the new alias after initial creation")
                raise RuntimeError("Failed to obtain ID for the new alias after initial creation.")

            generated_short_code = AliasService._generate_short_code(created_alias.id)
            self.logger.debug(f"Generated short code: {generated_short_code} for alias ID: {created_alias.id}")

            repo_update_data = AliasRepoUpdate(short_code=generated_short_code)
            final_alias = await self.alias_repository.update(db_obj=created_alias, obj_in=repo_update_data)

            self.logger.info(
                f"Successfully created alias with ID: {final_alias.id}, short_code: {final_alias.short_code}"
            )
            return final_alias

        except Exception as e:
            self.logger.error(f"Failed to create alias for URL {alias_create_request.target_url}: {str(e)}")
            raise

    async def get_user_aliases(
        self, user_id: int, active_only: bool = False, limit: int = 100, offset: int = 0
    ) -> List[Alias]:
        """Get aliases for a specific user with pagination."""
        self.logger.info(
            f"Fetching aliases for user {user_id}, active_only: {active_only}, limit: {limit}, offset: {offset}"
        )

        try:
            aliases = await self.alias_repository.get_user_aliases(
                user_id=user_id, active_only=active_only, limit=limit, offset=offset
            )
            self.logger.info(f"Successfully fetched {len(aliases)} aliases for user {user_id}")
            return aliases

        except Exception as e:
            self.logger.error(f"Failed to fetch aliases for user {user_id}: {str(e)}")
            raise

    async def deactivate_alias_by_short_code(self, short_code: str, user_id: int) -> Optional[Alias]:
        """Deactivate an alias by short code if it belongs to the user."""
        self.logger.info(f"Deactivating alias with short code {short_code} for user {user_id}")

        try:
            alias = await self.alias_repository.get_by_short_code_and_user(short_code=short_code, user_id=user_id)
            if not alias:
                self.logger.warning(f"Alias with short code {short_code} not found for user {user_id}")
                return None

            update_data = AliasRepoUpdate(is_enabled=False)
            updated_alias = await self.alias_repository.update(db_obj=alias, obj_in=update_data)
            self.logger.info(f"Successfully deactivated alias with short code {short_code}")
            return updated_alias

        except Exception as e:
            self.logger.error(f"Failed to deactivate alias {short_code} for user {user_id}: {str(e)}")
            raise

    async def get_target_url_by_short_code(self, short_code: str) -> Optional[str]:
        """Get target URL for a short code if the alias is active."""
        self.logger.debug(f"Looking up target URL for short code: {short_code}")

        alias = await self.get_active_alias_by_short_code(short_code)
        if not alias:
            return None

        self.logger.info(f"Successfully resolved short code {short_code} to URL: {alias.target_url}")
        return alias.target_url

    async def get_active_alias_by_short_code(self, short_code: str) -> Optional[Alias]:
        """Get active alias by short code for statistics collection."""
        self.logger.debug(f"Looking up active alias for short code: {short_code}")

        try:
            alias = await self.alias_repository.get_by_short_code(short_code)
            if not alias:
                self.logger.warning(f"No alias found for short code: {short_code}")
                return None

            if not alias.is_enabled:
                self.logger.warning(f"Alias {alias.id} is disabled for short code: {short_code}")
                return None

            if alias.expires_at and alias.expires_at < datetime.now(timezone.utc):
                self.logger.warning(f"Alias {alias.id} has expired for short code: {short_code}")
                return None

            self.logger.info(f"Successfully found active alias {alias.id} for short code: {short_code}")
            return alias

        except Exception as e:
            self.logger.error(f"Error looking up alias for short code {short_code}: {str(e)}")
            raise

    @staticmethod
    def _generate_short_code(alias_id: int) -> str:
        return generate_short_code_from_id(alias_id)
