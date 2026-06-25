from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "karynos-backend"
    CORS_ORIGINS: str = "http://localhost:3000"

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    POSTHOG_PROJECT_TOKEN: str = ""
    POSTHOG_HOST: str = "https://us.i.posthog.com"
    POSTHOG_DISABLED: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
