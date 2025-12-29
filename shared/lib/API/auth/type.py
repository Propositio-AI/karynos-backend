from pydantic import BaseModel

class AccessUser(BaseModel):
    sub: str
    email: str
    account_type: str