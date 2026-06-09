from uuid import UUID

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    job_id: str


class CreateConversationDB(BaseModel):
    owner_id: UUID
    job_id: str
    job_name: str
    assistant_gender: str
    assistant_name: str


class NewMessageRequest(BaseModel):
    role: str
    text_content: str


class NewUserMessageDB(BaseModel):
    conversation_id: str
    sender_id: str
    role: str
    text_content: str


class NewAIMessageDB(BaseModel):
    conversation_id: str
    sender_id: str
    role: str
    text_content: str
