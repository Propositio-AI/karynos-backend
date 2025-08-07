import uuid
from datetime import datetime
from pydantic import BaseModel

class AuthTableSchema(BaseModel):
    id: uuid.UUID = None
    email:str
    token: uuid.UUID = None
    created_at: datetime = None
    expires_at: datetime = None
    used_at: datetime = None

class MailSchema(BaseModel):
    email: str