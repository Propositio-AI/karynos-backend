# Config

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service Name
    SERVICE_NAME:str

    PREFIX:str
    TAG:str

    COGNITO_REGION: str
    USER_POOL_ID: str
    CLIENT_ID: str
    CLIENT_SECRET: str

settings = Settings()