import boto3
from fastapi import HTTPException, status
import hashlib
import hmac
import base64

from core.config import settings

COGNITO_REGION = settings.COGNITO_REGION
USER_POOL_ID = settings.USER_POOL_ID
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET

client = boto3.client("cognito-idp", region_name=COGNITO_REGION)

def get_secret_hash(username):
    message = username + CLIENT_ID
    dig = hmac.new(
        CLIENT_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def authenticate_user(username: str, password: str):
    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": get_secret_hash(username)
            }
        )

        # パスワード更新用
        # res = client.respond_to_auth_challenge(
        #     ClientId=CLIENT_ID,
        #     ChallengeName="NEW_PASSWORD_REQUIRED",
        #     Session=response['Session'],
        #     ChallengeResponses={
        #         "USERNAME": username,
        #         "NEW_PASSWORD": "StrongP@ssw0rd!",
        #         "userAttributes.given_name": "Yuta",
        #         "userAttributes.family_name": "Kageyama",
        #         "userAttributes.nickname": "Yuta",
        #         "SECRET_HASH": get_secret_hash(username)
        #     }
        # )

        # print(res, flush=True)

        return response['AuthenticationResult']
    
    except client.exceptions.NotAuthorizedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    except client.exceptions.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )   