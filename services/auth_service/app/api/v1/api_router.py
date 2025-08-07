# Routing file

from fastapi import APIRouter, Cookie

from schemas.AuthSchema import MailSchema
from api.v1.endpoints.send import send
from api.v1.endpoints.verify import verify, verify_login
from api.v1.endpoints.refresh import refrsh_access_token

router = APIRouter()

# verify JWT
@router.get("/verify")
async def _(token:str):
    return verify(token)

# Refresh Access Token
@router.post("/refresh")
async def _(refresh_token: str = Cookie(None)):
    return refrsh_access_token(refresh_token)

# Sending mail
@router.post("/mail")
async def _(data: MailSchema):    
    auth = send(data.email)

    return {
        "email": auth.email,
        "created_at": auth.created_at,
        "expires_at": auth.expires_at
        }


# verify Login
@router.get("/login")
async def _(token:str):
    is_new_user, token = verify_login(token)

    return {
        "is_new": is_new_user,
        "access_token": token
    }
