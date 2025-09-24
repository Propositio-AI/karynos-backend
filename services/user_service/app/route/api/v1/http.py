
from fastapi import APIRouter, Depends, HTTPException

from crud.User import user_crud
from shared.lib.auth import auth

# /api/v1/user
router = APIRouter()

# Add User
@router.post("/")
async def _(user_id = Depends(auth)):
    # TODO : 基本的にユーザーの作成にはトークンが必要になるが、トークンIDがguestのときのみ作成する（大量にアカウントを）
    print(user_id)
    return user_id

# Get User
@router.get("/")
async def _(email: str = None):
    success, users, error = user_crud.read([
        ["email", "==", email]
    ])

    if not success:
        return HTTPException(status_code=500, detail=error)

    user = users[0]
    return(
        user.id,
        {
            "last_name": user.last_name,
            "first_name": user.first_name,
            "email": user.email,
            "user_type": user.user_type, 
            "grade": user.grade,
            "class_no": user.class_no,
            "student_no": user.student_no,   
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at
        }
    )

@router.put("/")
async def newUser():
    pass