# User Table

from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, VARCHAR, INTEGER

from models import Base

from utils.time import get_utc_time

class UserTypeTable(Base):
    __tablename__ = "user_type"

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
        nullable=True,
        server_onupdate=get_utc_time
    )

    __table_args__ = (
        Index("id", id),
    )