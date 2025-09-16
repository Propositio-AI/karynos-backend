from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, JSON, UUID, FLOAT
from pydantic import BaseModel

from shared.utils.time import get_utc_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models import Base

class MemoTable(Base):
    __tablename__ = "memo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    archive_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    drawing_data = Column(JSON)
    canvas_w = Column(FLOAT)   
    canvas_h = Column(FLOAT)    
    created_at = Column(DateTime, default=get_utc_time)
    updated_at = Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

MemoTableSchema: BaseModel = sqlalchemy_to_pydantic(MemoTable)
