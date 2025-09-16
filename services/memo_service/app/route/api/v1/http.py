from fastapi import APIRouter
from crud.Memo import memo_crud
from models.MemoTable import MemoTableSchema

# /api/v1/memo
router = APIRouter()

@router.get("/", response_model=list[MemoTableSchema])
async def getMemo(archive_id: str):
    # TODO: ユーザーIDの取得処理
    user_id = ""

    memos = memo_crud.read([
        ["archive_id", "==", archive_id]
        ["user_id", "==", user_id]
    ])

    return memos

@router.post("/", response_model=MemoTableSchema)
async def newMemo(data: MemoTableSchema):
    # TODO: ユーザーIDの取得処理
    user_id = ""

    new_memo.user_id = user_id
    new_memo = memo_crud.create(data)
    
    return new_memo

@router.put("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str, data: MemoTableSchema):
    updated_memos = memo_crud.update(
        [
            ["id", "==", memo_id]
        ],
        data
    )

    return updated_memos

@router.delete("/{memo_id}", response_model=list[MemoTableSchema])
async def newUser(memo_id: str):
    deleted_memos = memo_crud.delete([
        ["id", "==", memo_id]
    ])

    return deleted_memos

