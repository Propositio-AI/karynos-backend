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

class DreamerGroupTable(Base):
    __tablename__ = "dreamer_groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    name = Column(VARCHAR, nullable=False)
    description = Column(VARCHAR)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    members = relationship("DreamerGroupMember", back_populates="group")


DreamerGroupTableSchema: BaseModel = sqlalchemy_to_pydantic(DreamerGroupTable)
