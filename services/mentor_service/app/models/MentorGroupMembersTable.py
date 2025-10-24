from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    VARCHAR,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MentorGroupMembersTable(Base):
    __tablename__ = "mentor_group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    group_id = Column(UUID(as_uuid=True), ForeignKey("mentor_groups.group_id"), nullable=False, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.mentor_id"), nullable=False, index=True)
    role = Column(VARCHAR, nullable=False)
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)

    group = relationship("MentorGroup", back_populates="members")
    mentor = relationship("Mentor", back_populates="memberships")



MentorGroupMemberTableSchema: BaseModel = sqlalchemy_to_pydantic(MentorGroupMembersTable)