from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from url_alias.db.database import Base


class BaseModel(Base):
    """Base model for all models with common fields"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def dict(self) -> dict[str, Any]:
        """Convert model to dict"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self) -> str:
        """String representation of model"""
        attrs = [f"{key}={value}" for key, value in self.dict().items() if not key.startswith("_")]
        return f"{self.__class__.__name__}({', '.join(attrs)})"
