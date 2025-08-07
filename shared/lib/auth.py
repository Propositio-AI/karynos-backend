from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from shared.lib.api_client import HTTP_APIClient

security = HTTPBearer()

def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("Sending AUth")
    token = credentials.credentials
    client = HTTP_APIClient(key = token)
    user_id = client.get("http://auth-service:8000/auth/")

    return user_id
