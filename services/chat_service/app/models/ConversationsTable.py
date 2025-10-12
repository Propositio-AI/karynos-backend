from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import (
    VARCHAR,
    UUID,
    INTEGER,
    TIMESTAMP
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class ConversationsTable(Base):
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(VARCHAR, nullable=False)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default="NOW()")

    # リレーション
    messages = relationship("Message", back_populates="conversation")
    participants = relationship("ConversationParticipant", back_populates="conversation")


ConversationsTableSchema: BaseModel = sqlalchemy_to_pydantic(ConversationsTable)
