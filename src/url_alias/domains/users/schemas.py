from pydantic import Field

from url_alias.db.schema import AppBaseSchema, BaseSchema


class UserBase(AppBaseSchema):
    """Base schema for User, shared properties."""

    username: str = Field(..., min_length=3, max_length=100, examples=["john_doe"])


class UserCreate(UserBase):
    """Schema for user creation. Will be used by API, password will be hashed by service."""

    password: str = Field(..., min_length=8, examples=["S3cr3tP@sswOrd"])


class UserRead(UserBase, BaseSchema):
    """Schema for reading user details. Represents a user in API responses."""

    is_active: bool = Field(..., description="Whether the user is currently active.")
