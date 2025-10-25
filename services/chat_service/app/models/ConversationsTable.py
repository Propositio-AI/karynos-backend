from sqlalchemy.schema import Column
from sqlalchemy.types import (
    TEXT,
    UUID,
    DateTime,
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum, text
from sqlalchemy import func

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class ShareType(PyEnum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"

class ConversationsTable(Base):
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(TEXT, nullable=False)
    share_type = Column(SQLEnum(ShareType, name="share_type", create_type=False), nullable=False, server_default=text("'PRIVATE'"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    messages = relationship("Message", back_populates="conversation")
    participants = relationship("ConversationParticipant", back_populates="conversation")


ConversationsTableSchema: BaseModel = sqlalchemy_to_pydantic(ConversationsTable)
