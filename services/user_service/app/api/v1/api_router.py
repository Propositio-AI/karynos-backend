# Routing file

from fastapi import APIRouter, Depends

from schemas.UserSchema import newUserSchema
from api.v1.endpoints.user import get_user
from shared.lib.auth import auth

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
    user = get_user(email=email)

    # TODO : ここの処理どうにかしたい
    if user is None:
        return None
    
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