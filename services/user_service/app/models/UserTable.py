# User Table

from uuid6 import uuid7

from sqlalchemy.schema import Column
from sqlalchemy import Index, ForeignKey
from sqlalchemy.types import DateTime, VARCHAR, UUID, INTEGER

from models.base import Base

from shared.utils.time import get_utc_time

class UserTable(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid7
    )
    last_name = Column(
        VARCHAR,
        nullable=True
    )
    first_name = Column(
        VARCHAR,
        nullable=False
    )
    email = Column(
        VARCHAR,
        nullable=False,
        unique=True
    )
    user_type = Column(
        INTEGER,
        ForeignKey("user_type.id"),
        nullable=True,
    )
    grade = Column(
        INTEGER,
        nullable=True
    )
    class_no = Column(
        INTEGER,
        nullable=True
    )
    student_no = Column(
        INTEGER,
        nullable=True
    )
    school = Column(
        UUID(as_uuid=True),
        nullable=True
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
    last_login_at = Column(
        DateTime,
        nullable=True
    )

    # __table_args__ = (
    #     Index("user_id", id),
    #     Index("email", email),
    # )