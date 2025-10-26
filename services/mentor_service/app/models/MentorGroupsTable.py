from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    TEXT,
    UUID,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MentorGroupsTable(Base):
    __tablename__ = "mentor_groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    chief_mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.mentor_id"), nullable=False)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

MentorGroupTableSchema: BaseModel = sqlalchemy_to_pydantic(MentorGroupsTable)
