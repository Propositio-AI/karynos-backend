# Auth Table 

from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, VARCHAR, UUID
from pydantic import BaseModel

from shared.utils.time import get_utc_time, get_expires_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base


class AuthTable(Base):
    __tablename__ = "auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    email = Column(VARCHAR)
    token = Column(VARCHAR)
    created_at = Column(DateTime, default=get_utc_time)
    expires_at = Column(DateTime, default=get_expires_time(minute=15))
    used_at = Column(DateTime)

AuthTableSchema: BaseModel = sqlalchemy_to_pydantic(AuthTable)
