# Routing file

import uuid
from fastapi import APIRouter
from schemas.QuerySchema import newQuerySchema, updateQuerySchema

from api.v1.endpoints.query import add_query

router = APIRouter()

@router.get("/")
async def getQuery(query_id: uuid.UUID):
    pass

@router.post("/")
async def _(data: newQuerySchema):   
    return add_query(data)

@router.put("/{query_id}")
async def updateQuery(data: updateQuerySchema):
    pass

@router.delete("/{query_id}")
async def deleteQuery():
    pass


