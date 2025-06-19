# User Table

from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index
from sqlalchemy.types import DateTime, JSON, UUID, FLOAT

from models import Base

from utils.time import get_utc_time

class MemoTable(Base):
    __tablename__ = "memo"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    query_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )
    drawing_data = Column(
        JSON,
        nullable=False
    )
    canvas_w = Column(
        FLOAT,
        nullable=False
    )    
    canvas_h = Column(
        FLOAT,
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
        Index("query_and_user", query_id, user_id),
    )