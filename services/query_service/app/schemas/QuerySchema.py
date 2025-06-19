import uuid
from datetime import datetime
from pydantic import BaseModel

class QuerySchema(BaseModel):
    id: uuid.UUID = None
    user_id: uuid.UUID = None
    type: int = None
    archvie_id: uuid.UUID = None
    favorite: bool = None
    created_at: datetime = None
    updated_at: datetime = None

class newQueryModel(BaseModel):
    query: str
    type: int
    archive_id: uuid.UUID

class updateQueryModel(BaseModel):
    favorite: bool