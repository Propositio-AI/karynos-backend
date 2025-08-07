from fastapi import Header

from core.config import settings
from crud.Auth import read_valid_token
from shared.lib.api_client import HTTP_APIClient
from lib.security import JWT_SERVICE


jwt_service = JWT_SERVICE()

def verify(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ").strip()
    return jwt_service.verify_jwt_token(token)

def verify_login(token: str):
    valid_token = read_valid_token(token = token)

    client = HTTP_APIClient()


    # トークン認証成功
    if valid_token is not None:
        email = valid_token.email
        user_id, _ = client.get("http://user-service:8000/user", params={"email": email})

        if user_id is None:
            # 新規会員登録時

            temp_token = jwt_service.generate_access_token("guest", settings.CURRENT_JWT_KEY_ID)

            return True, temp_token
        else:
            # 既存会員登録時

            token = jwt_service.generate_access_token(user_id, settings.CURRENT_JWT_KEY_ID) 
            return False,  token        

    return False, None
