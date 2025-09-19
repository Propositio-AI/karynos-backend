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

@router.post("/", response_model=QueryTableSchema)
async def _(data: QueryTableSchema):
    # TODO: ユーザーID取得処理
    data.user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    return query_crud.create(data)