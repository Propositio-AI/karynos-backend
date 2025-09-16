from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, UUID, VARCHAR
from pydantic import BaseModel

from shared.utils.time import get_utc_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models import Base

class MailTable(Base):
    __tablename__ = "mail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    to_email = Column(VARCHAR)
    title = Column(VARCHAR)
    contents = Column(VARCHAR)
    status = Column(VARCHAR, default="PENDING")
    created_at = Column(DateTime, default=get_utc_time)
    updated_at = Column(DateTime, default=get_utc_time, onupdate=get_utc_time)

MailTableSchema: BaseModel = sqlalchemy_to_pydantic(MailTable)
