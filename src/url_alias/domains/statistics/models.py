from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from url_alias.db.model import BaseModel


class AliasStatistic(BaseModel):
    __tablename__ = "alias_statistics"

    alias_id: Mapped[int] = mapped_column(Integer, ForeignKey("aliases.id"), nullable=False, unique=True, index=True)
    total_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_hour_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_day_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_hour_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_day_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    alias = relationship("Alias", back_populates="statistics")
