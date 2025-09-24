# Routing file

from fastapi import APIRouter, Cookie, Header, HTTPException

from uuid import uuid4

from models.AuthTable import AuthTableSchema

from crud.Auth import auth_crud
from shared.utils.time import get_utc_time

from shared.lib.api_client import HTTP_APIClient
from lib.security import JWT_SERVICE
from core.config import settings

# /api/v1/auth
router = APIRouter()

jwt_service = JWT_SERVICE()

# verify JWT
@router.get("/verify")
async def _(token:str = Header(...)):
    # ここあってる？
    token = token.removeprefix("Bearer ").strip()
    return jwt_service.verify_jwt_token(token)

# Refresh Access Token
@router.post("/refresh")
async def _(refresh_token: str = Cookie(None)):
    user_id = jwt_service.verify_jwt_token(refresh_token)

    # TODO : User IDがなかった際のエラー処理
    new_access_token = jwt_service.generate_access_token(user_id, settings.CURRENT_JWT_KEY_ID)

    return {"access_token": new_access_token}

# Sending mail
@router.post("/mail")
async def _(data: AuthTableSchema):
    data.token = uuid4()    
    success, auth, error = auth_crud.create(data)

    if not success:
        HTTPException(status_code=500, detail=error)
        
    return {
        "email": auth.email,
        "created_at": auth.created_at,
        "expires_at": auth.expires_at
    }
    
# verify Login
@router.get("/login")
async def _(token:str):
    success, valid_tokens, error = auth_crud.read([
        ["token", "==", token],
        ["expires_at", ">=", get_utc_time()],
        ["used_at", "==", None]
    ])

    if not success:
        # HTTPException(status_code=500, detail=error)
        pass

    if not len(valid_tokens): return {
        "is_new": False,
        "access_token": None
    }

    valid_token = valid_tokens[0]

    client = HTTP_APIClient()

    # トークン認証成功
    if valid_token is not None:
        email = valid_token.email
        user_id, _ = client.get("http://user-service:8000/user", params={"email": email})

        if user_id is None:
            # 新規会員登録時

            temp_token = jwt_service.generate_access_token("guest", settings.CURRENT_JWT_KEY_ID)
            
            return {
                "is_new": True,
                "access_token": temp_token
            }

        else:
            # 既存会員登録時

            token = jwt_service.generate_access_token(user_id, settings.CURRENT_JWT_KEY_ID) 
            return {
                "is_new": False,
                "access_token": token
            }
            
    return {
        "is_new": False,
        "access_token": None
    }
