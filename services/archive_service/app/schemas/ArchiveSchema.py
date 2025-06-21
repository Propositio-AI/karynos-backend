import uuid
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

# TODO: Contentsの型を定義する

class ArchiveSchema(BaseModel):
    id: uuid.UUID = None
    type: int 
    share_type: int
    contents: Dict[str, str]
    contents_metadata: Dict[str, str]
    created_at: datetime = None

class newArchiveModel(BaseModel):
    type: int
    contents: Dict[str, str]
    contents_metadata: Dict[str, str]