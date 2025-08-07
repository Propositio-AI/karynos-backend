from pathlib import Path 
from datetime import datetime, timezone
from uuid import UUID
import jwt
import json
from datetime import timedelta

from core.config import settings
from shared.utils.file import read_file
from shared.utils.time import get_utc_time

class JWT_SERVICE():
    def __init__(self):
        private_key_folder_path = Path(f"{settings.PRIVATE_KEY_FOLDER_PATH}/key.json")
        keys = json.loads(read_file(private_key_folder_path))

        self.key_pair = {}

        for key in keys["keys"]:
            # TODO: キーID自体の有効期限の確認
            
            private_key_path = Path(f"{settings.PRIVATE_KEY_FOLDER_PATH}/{key["name"]}")
            self.key_pair[key["kid"]] = {
                "alg": key["alg"],
                "key": private_key_path.read_text(encoding="utf-8")
            }

    def generate_jwt_rs256(
        self,
        user_id: UUID,
        expires_at: datetime,
        kid: str
    ) -> str:
        
        payload = {
            "exp": int(expires_at.replace(tzinfo=timezone.utc).timestamp()),
            "user_id": str(user_id),
        }
        headers = {"kid": kid} if kid else None

        return jwt.encode(payload, self.key_pair[kid]["key"], algorithm=self.key_pair[kid]["alg"], headers=headers)
    
    def generate_access_token(self, user_id: UUID, kid: str) -> str:
        expires_at = get_utc_time() + timedelta(minutes=15)
        return self.generate_jwt_rs256(user_id, expires_at, kid)

    def generate_refresh_token(self, user_id: UUID, kid: str) -> str:
        expires_at = get_utc_time() + timedelta(days=7)
        return self.generate_jwt_rs256(user_id, expires_at, kid)
    
    def verify_jwt_token(self, token: str):
        # TODO: エラー処理をきれいに統一する

        try:
            header = jwt.get_unverified_header(token)

            kid = header.get("kid")
            payload = jwt.decode(
                token,
                self.key_pair[kid]["key"],
                algorithms=[self.key_pair[kid]["alg"]],             
            )

            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
