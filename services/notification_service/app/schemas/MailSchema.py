import uuid
from datetime import datetime
from pydantic import BaseModel

class QuerySchema(BaseModel):
    id: uuid.UUID = None
    to_email: str
    title: str
    contents: str = "Pending"
    status: str = None
    created_at: datetime = None
    updated_at: datetime = None

class newMailModel(BaseModel):
    to_email: str
    title: str
    contents: str
