from fastapi import Header

from core.config import settings
from lib.security import JWT_SERVICE

jwt_service = JWT_SERVICE()

def refrsh_access_token(refresh_token: str):
    user_id = jwt_service.verify_jwt_token(refresh_token)

    # TODO : User IDがなかった際のエラー処理
    new_access_token = jwt_service.generate_access_token(user_id, settings.CURRENT_JWT_KEY_ID)

    return {"access_token": new_access_token}