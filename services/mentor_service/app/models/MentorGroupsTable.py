from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    VARCHAR,
    UUID,
    TIMESTAMP
)
from pydantic import BaseModel
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MentorGroupTable(Base):
    __tablename__ = "mentor_groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    chief_mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.mentor_id"), nullable=False)
    name = Column(VARCHAR, nullable=False)
    description = Column(VARCHAR)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    chief_mentor = relationship("Mentor", back_populates="groups")
    members = relationship("MentorGroupMember", back_populates="group")


MentorGroupTableSchema: BaseModel = sqlalchemy_to_pydantic(MentorGroupTable)
