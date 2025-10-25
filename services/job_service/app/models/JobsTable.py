from sqlalchemy.schema import Column
from sqlalchemy.types import (
    DateTime,
    INTEGER
)
from pydantic import BaseModel
from sqlalchemy import func

from shared.utils.time import get_utc_time
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class JobsTable(Base):
    __tablename__ = "jobs"

    job_id = Column(INTEGER, primary_key=True, autoincrement=True)
    title = Column(INTEGER(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    


JobTableSchema: BaseModel = sqlalchemy_to_pydantic(JobsTable)
