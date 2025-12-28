from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    DateTime,
    TEXT
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import func
from pydantic import BaseModel
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class RoleType(PyEnum):
    user = "user"
    assistant = "assistant"
    system = "system"

class MessagesTable(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    role = Column(SQLEnum(RoleType, name="role_type", create_type=False), nullable=False)
    text_content = Column(TEXT, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    # conversation = relationship("Conversation", back_populates="messages")

MessagesTableSchema: BaseModel = sqlalchemy_to_pydantic(MessagesTable)