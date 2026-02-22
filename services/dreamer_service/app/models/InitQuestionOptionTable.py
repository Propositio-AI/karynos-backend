from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    TEXT,
    INTEGER,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base


class InitQuestionOptionTable(Base):
    __tablename__ = "init_question_options"

    option_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    question_id = Column(UUID(as_uuid=True), ForeignKey("init_questions.question_id"), nullable=False, index=True)
    option_order = Column(INTEGER, nullable=False)
    option_text = Column(TEXT, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


InitQuestionOptionTableSchema: BaseModel = sqlalchemy_to_pydantic(InitQuestionOptionTable)
