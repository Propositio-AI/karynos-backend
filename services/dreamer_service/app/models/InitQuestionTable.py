from sqlalchemy.schema import Column
from sqlalchemy.types import (
    UUID,
    TEXT,
    INTEGER,
    BOOLEAN,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base


class InitQuestionTable(Base):
    __tablename__ = "init_questions"

    question_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    version = Column(INTEGER, nullable=False, default=1)
    category = Column(TEXT, nullable=False, index=True)
    question_text = Column(TEXT, nullable=False)
    question_order = Column(INTEGER, nullable=False)
    is_active = Column(BOOLEAN, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


InitQuestionTableSchema: BaseModel = sqlalchemy_to_pydantic(InitQuestionTable)
