import uuid
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

# TODO: Contentsの型を定義する

class ArchiveTableSchema(BaseModel):
    id: uuid.UUID = None
    type: int
    share_type: int = 1
    contents: Dict[str, str] | None = None
    contents_metadata: Dict[str, str] | None = None
    created_at: datetime = None

class newArchiveSchema(BaseModel):
    type: int
    contents: Dict[str, str] | None = None
    contents_metadata: Dict[str, str] | None = None