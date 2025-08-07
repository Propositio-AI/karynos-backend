import uuid
from datetime import datetime
from pydantic import BaseModel

class QueryTableSchema(BaseModel):
    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    type: int | None = None
    archive_id: uuid.UUID | None = None
    favorite: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class newQuerySchema(BaseModel):
    query: str
    type: int
    archive_id: uuid.UUID | None = None
    
class updateQuerySchema(BaseModel):
    favorite: bool