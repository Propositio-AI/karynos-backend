from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, INTEGER, VARCHAR

from models.base import Base

from utils.time import get_utc_time

class ShareTable(Base):
    __tablename__ = "share_type"

    id = Column(
        INTEGER,
        primary_key=True,
        nullable=False,
    )
    type = Column(
        VARCHAR,
        nullable=False
    )
    share_type = Column(
        INTEGER,
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_onupdate=get_utc_time
    )

    __table_args__ = (
        Index("id", id),
    )