from fastapi import APIRouter, Response, status

from schema import LoginRequest
from lib.cognito import authenticate_user

from services.auth_service.app.schema import LoginResponse

# /api/v1/auth
router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    auth_result = authenticate_user(request.username, request.password)

    return LoginResponse(access_token=auth_result["IdToken"])

@router.post("/logout")
async def _(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return status.HTTP_200_OK