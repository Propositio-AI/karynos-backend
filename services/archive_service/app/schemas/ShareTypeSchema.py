from datetime import datetime
from pydantic import BaseModel

class ShareTypeSchema(BaseModel):
    id: int = None
    type: str 
    created_at: datetime = None
    updated_at: datetime = None
