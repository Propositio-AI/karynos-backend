from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    VARCHAR,
    TIMESTAMP,
    TEXT
)
from pydantic import BaseModel
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class MessagesTable(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(VARCHAR, nullable=False)
    text_content = Column(TEXT, nullable=False)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    conversation = relationship("Conversation", back_populates="messages")

MessagesTableSchema: BaseModel = sqlalchemy_to_pydantic(MessagesTable)