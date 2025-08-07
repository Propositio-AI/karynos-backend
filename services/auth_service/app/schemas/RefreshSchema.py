import uuid
from datetime import datetime
from pydantic import BaseModel

class RefreshTableSchema(BaseModel):
    id: uuid.UUID = None
    token: uuid.UUID = None
    created_at: datetime = None
    expires_at: datetime = None
    used_at: datetime = None