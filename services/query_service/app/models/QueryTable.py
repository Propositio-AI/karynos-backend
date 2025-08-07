from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index, ForeignKey
from sqlalchemy.types import DateTime, UUID, INTEGER, BOOLEAN

from models.base import Base

from shared.utils.time import get_utc_time

class QueryTable(Base):
    __tablename__ = "query"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )
    type = Column(
        INTEGER,
        ForeignKey("query_type.id"),
        nullable=False
    )
    archive_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )
    favorite = Column(
        BOOLEAN,
        nullable=False,
        default=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time,
        onupdate=get_utc_time
    )

    __table_args__ = (
        Index("query_id", id),
        Index("user_id", user_id),
    )