from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import INTEGER, TEXT, DateTime
from sqlalchemy import func
from pydantic import BaseModel
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class JobsTable(Base):
    __tablename__ = "jobs"

    job_id = Column(INTEGER, primary_key=True, autoincrement=True)
    industry_id = Column(INTEGER, ForeignKey("industries.industry_id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(INTEGER, ForeignKey("job_categories.category_id", ondelete="RESTRICT"), nullable=False)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

JobsTableSchema: BaseModel = sqlalchemy_to_pydantic(JobsTable)
