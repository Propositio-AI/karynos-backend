from uuid import uuid4

from crud.Auth import create_token
from schemas.AuthSchema import AuthTableSchema

def send(email: str):
    new_token = create_token(AuthTableSchema(token = uuid4(), email = email))

    return new_token