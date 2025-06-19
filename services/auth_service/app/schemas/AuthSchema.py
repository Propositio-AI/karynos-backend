import uuid
from datetime import datetime
from pydantic import BaseModel

class AuthSchema(BaseModel):
    id: uuid.UUID = None
    email:str
    token: uuid.UUID = None
    created_at: datetime = None
    expires_at: datetime = None
    used_at: datetime = None

class MailModel(BaseModel):
    email: str