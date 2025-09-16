# Refresh Table

from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, VARCHAR, UUID
from pydantic import BaseModel

from shared.utils.time import get_utc_time, get_expires_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class RefreshTable(Base):
    __tablename__ = "refresh"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    token = Column(VARCHAR)
    created_at = Column(DateTime, default=get_utc_time)
    expires_at = Column(DateTime, default=get_expires_time(month=3))
    used_at = Column(DateTime)

RefreshTableSchema: BaseModel = sqlalchemy_to_pydantic(RefreshTable)
