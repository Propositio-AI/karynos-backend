# Auth Table 

from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.types import DateTime, VARCHAR, UUID

from models.base import Base
from core.config import settings
from shared.utils.time import get_utc_time
from utils.expire_time import default_expires_at

class AuthTable(Base):
    __tablename__ = "auth"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    email = Column(
        VARCHAR,
        nullable=False
    )
    token = Column(
        VARCHAR,
        unique=True,
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_utc_time
    )
    expires_at = Column(
        DateTime,
        nullable=False,
        default=default_expires_at
    )
    used_at = Column(
        DateTime,
        nullable=True,
        default=None
    )

    __table_args__ = (
        Index("auth_token", token),
        Index("idx_email_expires_at", email, expires_at),
        CheckConstraint(expires_at > created_at, name="expires_after_created"),
        CheckConstraint(used_at < expires_at, name="used_before_expires"),
    )