import uuid
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

# TODO: DrawingDataの型を定義する

class MemoSchema(BaseModel):
    id: uuid.UUID = None
    query_id: uuid.UUID 
    user_id: uuid.UUID
    drawing_data: Dict[str, str]
    canvas_w: float
    canvas_h: float
    created_at: datetime = None
    updated_at: datetime = None

class newMemoModel(BaseModel):
    query_id: uuid.UUID
    drawing_data: Dict[str, str]
    canvas_w: float
    canvas_h: float
