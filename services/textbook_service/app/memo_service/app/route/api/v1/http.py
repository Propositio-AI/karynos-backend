from fastapi import APIRouter, HTTPException, Depends
from crud.Memo import memo_crud
from models.MemoTable import MemoTableSchema
from shared.lib.auth import get_current_user_id_str

# /api/v1/memo
router = APIRouter()

@router.get("/{archive_id}", response_model=list[MemoTableSchema])
async def getMemo(
    archive_id: str,
    user_id: str = Depends(get_current_user_id_str)
):
    # 認証されたユーザーIDを使用

    response = memo_crud.read([
        ["archive_id", "==", archive_id],
        ["user_id", "==", user_id]
    ])

    if not response["success"]:
        HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]


@router.post("/", response_model=MemoTableSchema)
async def newMemo(
    data: MemoTableSchema,
    user_id: str = Depends(get_current_user_id_str)
):
    # 認証されたユーザーIDを使用
    data.user_id = user_id
    response = memo_crud.create(data)

    if not response["success"]:
        HTTPException(status_code=500, detail=response["message"])
    return response["data"]

@router.put("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str, data: MemoTableSchema):
    response = memo_crud.update(
        [
            ["id", "==", memo_id]
        ],
        data
    )

    if not response["success"]:
        HTTPException(status_code=500, detail=response["message"])

    return response["data"]

@router.delete("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str):
    response = memo_crud.delete([
        ["id", "==", memo_id]
    ])

    if not response["success"]:
        HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]
    

