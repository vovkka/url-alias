from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

from pydantic import Field, computed_field, field_validator

from url_alias.db.schema import AppBaseSchema, BaseSchema
from url_alias.domains.aliases.constants import DEFAULT_EXPIRY_DAYS, MAX_SHORT_CODE_LENGTH, MIN_SHORT_CODE_LENGTH


def validate_target_url(url: str) -> str:
    """Validate target URL to prevent open redirect attacks."""
    if len(url) > 2048:
        raise ValueError("URL too long (max 2048 characters)")

    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Invalid URL format")

    if not parsed.scheme:
        raise ValueError("URL must include protocol (http or https)")

    if parsed.scheme.lower() not in ["http", "https"]:
        raise ValueError("Only HTTP and HTTPS protocols are allowed")

    if not parsed.netloc:
        raise ValueError("URL must include domain")

    return url


class AliasBase(AppBaseSchema):
    """Base schema for Alias."""

    target_url: str = Field(..., examples=["https://example.com/very/long/url?for=sharing"])
    short_code: str = Field(
        ...,
        examples=["abcdef"],
        min_length=MIN_SHORT_CODE_LENGTH,
        max_length=MAX_SHORT_CODE_LENGTH,
        description="The unique short code for the alias.",
    )
    user_id: Optional[int] = Field(None, description="Identifier of the user who owns the alias, if any.")
    expires_at: Optional[datetime] = Field(None, description="Timestamp when the alias should expire.")
    is_enabled: bool = Field(default=True, description="Whether the alias is manually enabled. This is stored in DB.")

    @field_validator("target_url")
    @classmethod
    def validate_target_url_field(cls, v: str) -> str:
        return validate_target_url(v)


class AliasCreateRequest(AppBaseSchema):
    """Schema for creating a new alias via API."""

    target_url: str = Field(..., examples=["https://example.com/very/long/url?for=sharing"])
    expires_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=DEFAULT_EXPIRY_DAYS),
        description=f"Timestamp when the alias should expire. Defaults to {DEFAULT_EXPIRY_DAYS} day(s) from now.",
    )
    is_enabled: Optional[bool] = Field(
        True, description="Whether the alias should be manually enabled upon creation. Defaults to True."
    )

    @field_validator("target_url")
    @classmethod
    def validate_target_url_field(cls, v: str) -> str:
        return validate_target_url(v)


class AliasUpdateRequest(AppBaseSchema):
    """Schema for updating an existing alias via API. All fields are optional."""

    target_url: Optional[str] = Field(None, examples=["https://example.com/another/long/url"])
    expires_at: Optional[datetime] = Field(None, description="Timestamp when the alias should expire.")
    is_enabled: Optional[bool] = Field(None, description="Manually set the enabled status of the alias.")

    @field_validator("target_url")
    @classmethod
    def validate_target_url_field(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_target_url(v)
        return v


class AliasRead(BaseSchema):
    """Schema for representing an alias in API responses with full short_url."""

    target_url: str = Field(..., examples=["https://example.com/very/long/url?for=sharing"])
    short_url: str = Field(..., examples=["http://localhost:8000/abc123"], description="Full short URL for redirect")
    user_id: Optional[int] = Field(None, description="Identifier of the user who owns the alias")
    expires_at: Optional[datetime] = Field(None, description="Timestamp when the alias expires")
    is_enabled: bool = Field(..., description="Whether the alias is manually enabled")

    @computed_field(description="true if alias is manually enabled AND not expired.")
    @property
    def is_active(self) -> bool:
        if not self.is_enabled:
            return False
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False
        return True
