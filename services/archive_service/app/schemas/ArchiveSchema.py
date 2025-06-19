import uuid
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

# TODO: Contentsの型を定義する

class ArchiveSchema(BaseModel):
    id: uuid.UUID = None
    query_id: uuid.UUID 
    user_id: uuid.UUID
    drawing_data: Dict[str, str]
    canvas_w: float
    canvas_h: float
    created_at: datetime = None
    updated_at: datetime = None

class newArchiveModel(BaseModel):
    type: int
    contents: Dict[str, str]
    metadata: Dict[str, str]