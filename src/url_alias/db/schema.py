from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class AppBaseSchema(PydanticBaseModel):
    """Base schema for all Pydantic models in the application, provides common model_config."""

    model_config = ConfigDict(from_attributes=True, validate_by_name=True, validate_by_alias=True)


class BaseSchema(AppBaseSchema):
    """Base schema for reading existing DB objects, includes common DB fields."""

    id: int
    created_at: datetime
    updated_at: datetime


class BaseCreateSchema(AppBaseSchema):
    """
    Base schema for data structures used when creating new DB objects.
    """

    ...


class BaseUpdateSchema(AppBaseSchema):
    """
    Base schema for data structures used when updating existing DB objects.
    """

    ...
