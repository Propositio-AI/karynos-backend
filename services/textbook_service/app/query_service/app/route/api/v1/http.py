from fastapi import APIRouter, Depends, HTTPException

from models.QueryTable import QueryTableSchema

from crud.Query import query_crud

from shared.utils import convert_to_filter
from shared.lib.auth import get_current_user_id_str

# /api/v1/query
router = APIRouter()

@router.get("/", response_model=list[QueryTableSchema])
async def _(data: QueryTableSchema = Depends(), op = "=="):
    filters = convert_to_filter(data, op)
    response = query_crud.read(filters)

    if not response["success"]:
        HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]
    

@router.post("/", response_model=QueryTableSchema)
async def _(
    data: QueryTableSchema,
    user_id: str = Depends(get_current_user_id_str)
):
    # 認証されたユーザーIDを使用
    data.user_id = user_id

    response = query_crud.create(data)

    if not response["success"]:
        return HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]
    