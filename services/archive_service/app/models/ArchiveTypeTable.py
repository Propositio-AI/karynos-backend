from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, INTEGER, VARCHAR

from models.base import Base

from shared.utils.time import get_utc_time

class ArchiveTypeTable(Base):
    __tablename__ = "archive_type"

    id = Column(
        INTEGER,
        primary_key=True,
        nullable=False,
    )
    type = Column(
        VARCHAR,
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
        default = get_utc_time,
        onupdate=get_utc_time
    )

    __table_args__ = (
        Index("archive_type_id", id),
    )