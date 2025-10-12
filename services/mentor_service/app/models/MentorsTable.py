from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    VARCHAR,
    UUID,
    INTEGER,
    TIMESTAMP
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MentorTable(Base):
    __tablename__ = "mentors"

    mentor_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    chief_mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.mentor_id"))
    orgnaztion_id = Column(INTEGER, index=True)
    login_id = Column(VARCHAR, nullable=False, index=True)
    name_family = Column(VARCHAR, nullable=False)
    name_given = Column(VARCHAR, nullable=False)
    access_group = Column(UUID(as_uuid=True), index=True)
    last_login_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    chief_mentor = relationship("Mentor", remote_side=[mentor_id])
    groups = relationship("MentorGroup", back_populates="chief_mentor")
    memberships = relationship("MentorGroupMember", back_populates="mentor")


MentorTableSchema: BaseModel = sqlalchemy_to_pydantic(MentorTable)
