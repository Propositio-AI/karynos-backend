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

class DreamerGroupMembersTable(Base):
    __tablename__ = "dreamer_group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    group_id = Column(UUID(as_uuid=True), ForeignKey("dreamer_groups.group_id"), nullable=False, index=True)
    dreamer_id = Column(UUID(as_uuid=True), ForeignKey("dreamers.dreamer_id"), nullable=False, index=True)
    joined_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    group = relationship("DreamerGroup", back_populates="members")
    dreamer = relationship("Dreamer", back_populates="memberships")


DreamerGroupMembersTableSchema: BaseModel = sqlalchemy_to_pydantic(DreamerGroupMembersTable)
