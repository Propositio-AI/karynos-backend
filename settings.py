from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "karynos-backend"
    POSTGRES_USER: str = "karynos"
    POSTGRES_PASSWORD: str = "karynos"
    POSTGRES_DB: str = "karynos"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
