from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    UUID,
    TIMESTAMP
)
from pydantic import BaseModel
from sqlalchemy.orm import relationship

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base


class ConversationParticipantTable(Base):
    __tablename__ = "conversation_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    joined_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    conversation = relationship("Conversation", back_populates="participants")

ConversationParticipantTableSchema: BaseModel = sqlalchemy_to_pydantic(ConversationParticipantTable)
