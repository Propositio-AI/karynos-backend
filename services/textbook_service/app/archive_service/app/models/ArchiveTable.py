from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, UUID, JSON, TEXT
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from models.base import Base
from shared.utils.shema import sqlalchemy_to_pydantic

class ArchiveTable(Base):
    __tablename__ = "archive"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    query_id = Column(UUID(as_uuid=True))
    parent_id = Column(UUID(as_uuid=True))
    archive_type = Column(TEXT, default="CHAT")
    share_type = Column(TEXT, default="PRIVATE")
    archive_status = Column(TEXT, default="PENDING")
    contents = Column(JSON)
    contents_metadata = Column(JSON)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    

ArchiveTableSchema: BaseModel = sqlalchemy_to_pydantic(ArchiveTable)
