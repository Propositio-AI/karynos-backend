from fastapi import HTTPException, APIRouter

from shared.lib.basicError import errorWrapper, BasicError

# /api/v1/chat
router = APIRouter()

@router.get("/")
async def _(a: str):
    @errorWrapper("ApiKeyLimitExceeded")
    def handle():
        raise BasicError("AccountLocked")
        # return {"message": f"Hello {a}"}

    success, result, err = handle()
    
    if not success:
        raise  HTTPException(status_code = 500, detail=err)

    return result