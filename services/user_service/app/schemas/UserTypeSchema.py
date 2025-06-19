import uuid
from datetime import datetime
from pydantic import BaseModel

class UserTypeSchema(BaseModel):
    id: uuid.UUID = None
    type: str = None
    created_at: datetime = None
    updated_at: datetime = None