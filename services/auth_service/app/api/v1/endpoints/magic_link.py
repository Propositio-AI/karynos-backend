from crud.Auth import create_token
from core.security import gen_token
from schemas.AuthSchema import AuthSchema
from core.db import session

class SendMail:
    authData: AuthSchema

    def __init__(self, email):
        self.email = email

    def add_token(self):
        return create_token(
            db = session,
            data = AuthSchema(token=gen_token(), email=self.email)
        )

    def send(self):
        # Send mail using noification service
        pass
    