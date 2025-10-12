from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    VARCHAR,
    TIMESTAMP,
    INTEGER
)
from pydantic import BaseModel
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class DreamerTable(Base):
    __tablename__ = "dreamers"

    dreamer_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    orgnaztion_id = Column(INTEGER, index=True)
    login_id = Column(VARCHAR, nullable=False, index=True)
    name_family = Column(VARCHAR, nullable=False)
    name_given = Column(VARCHAR, nullable=False)
    last_login_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    memberships = relationship("DreamerGroupMember", back_populates="dreamer")



DreamerTableSchema: BaseModel = sqlalchemy_to_pydantic(DreamerTable)