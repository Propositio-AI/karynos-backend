from fastapi import APIRouter, Depends

from models.QueryTable import QueryTableSchema

from crud.Query import query_crud

from shared.utils import convert_to_filter

# /api/v1/query
router = APIRouter()

@router.get("/", response_model=list[QueryTableSchema])
async def _(data: QueryTableSchema = Depends(), op = "=="):
    filters = convert_to_filter(data, op)
    return query_crud.read(filters)