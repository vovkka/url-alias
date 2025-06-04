from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from url_alias.domains.aliases.dependencies import get_alias_service
from url_alias.domains.aliases.schemas import AliasCreateRequest, AliasRead
from url_alias.domains.aliases.services import AliasService
from url_alias.domains.users.dependencies import get_current_active_user
from url_alias.domains.users.models import User as UserModel

router = APIRouter(
    prefix="/aliases",
    tags=["aliases"],
)


def create_alias_read(alias, request: Request) -> AliasRead:
    """Helper function to create AliasRead with full short_url."""
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{alias.short_code}"

    return AliasRead(
        target_url=alias.target_url,
        short_url=short_url,
        user_id=alias.user_id,
        expires_at=alias.expires_at,
        is_enabled=alias.is_enabled,
        id=alias.id,
        created_at=alias.created_at,
        updated_at=alias.updated_at,
    )


@router.post("", response_model=AliasRead, status_code=status.HTTP_201_CREATED)
async def create_alias(
    request: Request,
    alias_create_request: AliasCreateRequest,
    alias_service: AliasService = Depends(get_alias_service),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Create a new URL alias. Requires Basic Auth.
    """
    try:
        created_alias_model = await alias_service.create_alias(
            alias_create_request=alias_create_request, user_id=current_user.id
        )

        return create_alias_read(created_alias_model, request)

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the alias.",
        )


@router.get("", response_model=List[AliasRead])
async def get_user_aliases(
    request: Request,
    alias_service: AliasService = Depends(get_alias_service),
    current_user: UserModel = Depends(get_current_active_user),
    active_only: bool = False,
    page: int = Query(default=1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
):
    """
    Get list of user's aliases with pagination. Requires Basic Auth.
    """
    try:
        offset = (page - 1) * page_size
        aliases = await alias_service.get_user_aliases(
            user_id=current_user.id, active_only=active_only, limit=page_size, offset=offset
        )
        return [create_alias_read(alias, request) for alias in aliases]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving aliases.",
        )


@router.patch("/{short_code}/deactivate", response_model=AliasRead)
async def deactivate_alias(
    request: Request,
    short_code: str,
    alias_service: AliasService = Depends(get_alias_service),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Deactivate a specific alias by short code. Requires Basic Auth.
    """
    try:
        updated_alias = await alias_service.deactivate_alias_by_short_code(
            short_code=short_code, user_id=current_user.id
        )

        if not updated_alias:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alias not found or you don't have permission to modify it.",
            )

        return create_alias_read(updated_alias, request)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deactivating the alias.",
        )
