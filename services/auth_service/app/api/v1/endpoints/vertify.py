from crud.Auth import get_valid_token
from core.db import session
from utils.time import get_utc_time

class Vertify:
    def __init__(self, token:str):
        self.token = token

    def vertify_token(self):
        vertify_time = get_utc_time()
        return get_valid_token(
            db=session,
            token=self.token,
            vertify_time=vertify_time
        )

    def create_jwt(self):
        pass
