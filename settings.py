import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "karynos-backend"
    CORS_ORIGINS: str = "http://localhost:3000"

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Amazon Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    AWS_REGION: str = "ap-northeast-1"

    # 認証スキップ（True にすると Cognito JWT 検証を完全にスキップしてモック値を返す）
    USE_MOCK_AUTH: bool = True

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_JOB_COLLECTION: str = "job_vector_db"

    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    # Dream Action
    DREAM_ACTION_MAX_TOKENS: int = 2000
    DREAM_ACTION_TIMEOUT_SECONDS: int = 120

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cognito_jwks_url(self) -> str:
        return (
            f"https://cognito-idp.{self.AWS_REGION}.amazonaws.com"
            f"/{self.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )

    @property
    def cognito_issuer(self) -> str:
        return (
            f"https://cognito-idp.{self.AWS_REGION}.amazonaws.com"
            f"/{self.COGNITO_USER_POOL_ID}"
        )

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
