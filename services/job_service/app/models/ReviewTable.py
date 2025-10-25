from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    DateTime,
    UUID,
    INTEGER
)
from pydantic import BaseModel
from sqlalchemy import func

from shared.utils.time import get_utc_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class JobReviewTable(Base):
    __tablename__ = "job_reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    job_id = Column(INTEGER, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(INTEGER(as_uuid=True), nullable=False)
    salary = Column(INTEGER, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    

JobReviewTableSchema: BaseModel = sqlalchemy_to_pydantic(JobReviewTable)