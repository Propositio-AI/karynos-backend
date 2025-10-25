from sqlalchemy.schema import Column
from sqlalchemy import func
from sqlalchemy.types import DateTime, UUID, TEXT
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models import Base

class MailTable(Base):
    __tablename__ = "mail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    to_email = Column(TEXT)
    title = Column(TEXT)
    contents = Column(TEXT)
    status = Column(TEXT, default="PENDING")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

MailTableSchema: BaseModel = sqlalchemy_to_pydantic(MailTable)
