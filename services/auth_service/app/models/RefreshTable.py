# Refresh Table

from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.types import DateTime, VARCHAR, UUID
from dateutil.relativedelta import relativedelta

from models import Base

from core.config import settings
from utils.time import get_utc_time

def default_expires_at():
    return get_utc_time() + relativedelta(month=settings.REFRESH_TOKEN_EXPIRES_MONTH)

class RefreshTable(Base):
    __tablename__ = "refresh"

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
        nullable=False
    )
    used_at = Column(
        DateTime,
        nullable=True
    )

    __table_args__ = (
        Index("idx_email_expires_at", email, expires_at),
        CheckConstraint(expires_at > created_at, name="expires_after_created"),
        CheckConstraint(used_at > expires_at, name="used_before_expires"),
    )