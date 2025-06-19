# Routing file

import uuid
from fastapi import APIRouter
from schemas.MemoSchema import newMemoModel

router = APIRouter()

@router.get("/")
async def getMemo(query_id: uuid.UUID):
    pass

@router.post("/")
async def newMemo(data: newMemoModel):
    pass

@router.put("/{memo_id}")
async def newUser(memo_id: uuid.UUID):
    pass

@router.delete("/{memo_id}")
async def newUser(memo_id: uuid.UUID):
    pass

