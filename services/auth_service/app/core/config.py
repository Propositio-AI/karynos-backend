# Config

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service Name
    SERVICE_NAME:str

    # API Setting
    PREFIX:str
    TAG:str

    # Auth Setting
    TOKEN_TOKEN_EXPIRES_MINUTES:int = 60
    REFRESH_TOKEN_EXPIRES_MONTH:int = 1

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str

    # Security
    PRIVATE_KEY_FOLDER_PATH: str
    CURRENT_JWT_KEY_ID: str

    @property
    def db_url(self) -> tuple:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"   

settings = Settings()