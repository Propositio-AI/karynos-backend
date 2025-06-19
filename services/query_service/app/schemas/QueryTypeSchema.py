from datetime import datetime
from pydantic import BaseModel

class QueryTypeSchema(BaseModel):
    id: int = None
    type: str 
    created_at: datetime = None
    updated_at: datetime = None
