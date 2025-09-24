from fastapi import APIRouter, HTTPException
from crud.Memo import memo_crud
from models.MemoTable import MemoTableSchema

# /api/v1/memo
router = APIRouter()

@router.get("/", response_model=list[MemoTableSchema])
async def getMemo(archive_id: str):
    # TODO: ユーザーIDの取得処理
    user_id = ""

    success, memos, error = memo_crud.read([
        ["archive_id", "==", archive_id]
        ["user_id", "==", user_id]
    ])

    if not success:
        HTTPException(status_code=500, detail=error)
    
    return memos


@router.post("/", response_model=MemoTableSchema)
async def newMemo(data: MemoTableSchema):
    # TODO: ユーザーIDの取得処理
    user_id = ""

    new_memo.user_id = user_id
    success, new_memo, error = memo_crud.create(data)

    if not success:
        HTTPException(status_code=500, detail=error)
    return new_memo

@router.put("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str, data: MemoTableSchema):
    success, updated_memos, error = memo_crud.update(
        [
            ["id", "==", memo_id]
        ],
        data
    )

    if not success:
        HTTPException(status_code=500, detail=error)

    return updated_memos

@router.delete("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str):
    success, deleted_memos, error = memo_crud.delete([
        ["id", "==", memo_id]
    ])

    if not success:
        HTTPException(status_code=500, detail=error)
    
    return deleted_memos
    

