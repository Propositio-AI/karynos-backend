from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, UUID, INTEGER, BOOLEAN, VARCHAR

from models import Base

from utils.time import get_utc_time

class MailTable(Base):
    __tablename__ = "mail"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    to_email = Column(
        VARCHAR,
        nullable=False
    )
    title = Column(
        VARCHAR,
        nullable=False
    )
    contents = Column(
        VARCHAR,
        nullable=True
    )
    status = Column(
        VARCHAR,
        nullable=False,
        default="PENDING"
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
        Index("status", status),
    )