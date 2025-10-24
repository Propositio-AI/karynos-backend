# User Table

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    DateTime,
    BOOLEAN,
    UUID,
    INTEGER
)
from pydantic import BaseModel
from sqlalchemy import func
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class HistoryTable(Base):
    __tablename__ = "history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    job_id = Column(INTEGER, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    dreamer_id = Column(UUID(as_uuid=True), nullable=False)
    good = Column(BOOLEAN, nullable=False, default=False)
    bad = Column(BOOLEAN, nullable=False, default=False)
    save = Column(BOOLEAN, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


HistoryTableSchema: BaseModel = sqlalchemy_to_pydantic(HistoryTable)
