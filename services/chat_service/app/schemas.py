from pydantic import BaseModel

class CreateConversationRequest(BaseModel):
    user_id: str
    job_id: str

class CreateConversationDB(BaseModel):
    owner_id: str
    job_id: str
    job_name: str
    assistant_gender: str
    assistant_name: str    

class NewMessageRequest(BaseModel):
    sender_id: str
    role: str
    text_content: str

class NewUserMessageDB(BaseModel):
    conversation_id: str
    sender_id: str
    role: str
    text_content: str

class NewAIMessageDB(BaseModel):
    conversation_id: str
    role: str
    text_content: str