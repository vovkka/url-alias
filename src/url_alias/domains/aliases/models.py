from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from url_alias.db.model import BaseModel


class Alias(BaseModel):
    __tablename__ = "aliases"

    target_url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    short_code: Mapped[Optional[str]] = mapped_column(String(12), unique=True, index=True, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    statistics = relationship("AliasStatistic", back_populates="alias", uselist=False)
