from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    TEXT,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MentorGroupMembersTable(Base):
    __tablename__ = "mentor_group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    group_id = Column(UUID(as_uuid=True), ForeignKey("mentor_groups.group_id"), nullable=False, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.mentor_id"), nullable=False, index=True)
    role = Column(TEXT, nullable=False)
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

MentorGroupMemberTableSchema: BaseModel = sqlalchemy_to_pydantic(MentorGroupMembersTable)