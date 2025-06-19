from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, UUID, INTEGER, BOOLEAN

from models import Base

from utils.time import get_utc_time

class queryTable(Base):
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
        server_onupdate=get_utc_time
    )

    __table_args__ = (
        Index("id", id),
        Index("user_id", user_id),
    )