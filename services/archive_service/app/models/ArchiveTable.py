from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, UUID, INTEGER, JSON

from models import Base

from utils.time import get_utc_time

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
        nullable=False
    )
    share_type = Column(
        INTEGER,
        nullable=False
    )
    contens = Column(
        JSON,
        nullable=False
    )
    metadata = Column(
        JSON,
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time
    )

    __table_args__ = (
        Index("id", id),
    )