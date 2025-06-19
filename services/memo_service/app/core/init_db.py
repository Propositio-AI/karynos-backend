# Create Sample DB Data

from schemas.MemoSchema import MemoSchema
from core.db import session

sampleMemo = [
    MemoSchema()
]