from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index, ForeignKey
from sqlalchemy.types import DateTime, UUID, INTEGER, JSON

from models.base import Base

from shared.utils.time import get_utc_time

class ArchiveTable(Base):
    __tablename__ = "archive"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    type = Column(
        INTEGER,
        ForeignKey("archive_type.id"),
        nullable=False
    )
    share_type = Column(
        INTEGER,
        ForeignKey("share_type.id"),
        nullable=False,
        default=0
    )
    contents = Column(
        JSON,
        nullable=True
    )
    contents_metadata = Column(
        JSON,
        nullable=True
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time
    )

    __table_args__ = (
        Index("archive_id", id),
    )