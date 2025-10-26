from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import func
from sqlalchemy.types import (
    UUID,
    DateTime
)
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base


class ConversationParticipantTable(Base):
    __tablename__ = "conversation_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    joined_at = Column(DateTime, server_default=func.now())

ConversationParticipantTableSchema: BaseModel = sqlalchemy_to_pydantic(ConversationParticipantTable)
