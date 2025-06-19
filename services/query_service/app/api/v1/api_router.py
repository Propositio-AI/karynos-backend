# Routing file

import uuid
from fastapi import APIRouter
from schemas.QuerySchema import newQueryModel, updateQueryModel

from endpoints.query import newQuery

router = APIRouter()

@router.get("/")
async def getQuery(query_id: uuid.UUID):
    pass

@router.post("/")
async def newQuery(data: newQueryModel):
    newQuery(data)

@router.put("/{query_id}")
async def updateQuery(data: updateQueryModel):
    pass

@router.delete("/{query_id}")
async def deleteQuery():
    pass


