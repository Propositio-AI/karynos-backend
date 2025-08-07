import uuid
from datetime import datetime
from pydantic import BaseModel

class UserTypeTableSchema(BaseModel):
    id: uuid.UUID = None
    type: str
    created_at: datetime = None
    updated_at: datetime = None