from url_alias.db.model import BaseModel
from url_alias.db.repository import BaseRepository
from url_alias.db.schema import AppBaseSchema, BaseCreateSchema, BaseSchema, BaseUpdateSchema
from url_alias.domains.aliases.models import Alias

# Import models to ensure they are registered with Base.metadata for Alembic
from url_alias.domains.users.models import User

__all__ = [
    "BaseModel",
    "BaseRepository",
    "AppBaseSchema",
    "BaseSchema",
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "User",
    "Alias",
]
