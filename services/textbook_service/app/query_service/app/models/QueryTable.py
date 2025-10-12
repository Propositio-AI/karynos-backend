from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, UUID, BOOLEAN, VARCHAR
from pydantic import BaseModel

from shared.utils.time import get_utc_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class QueryTable(Base):
    __tablename__ = "query"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    user_id = Column(UUID(as_uuid=True))
    parent_id = Column(UUID(as_uuid=True))
    query = Column(VARCHAR)
    query_type = Column(VARCHAR, default="CHAT")
    favorite = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=get_utc_time)
    updated_at = Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

QueryTableSchema: BaseModel = sqlalchemy_to_pydantic(QueryTable)
