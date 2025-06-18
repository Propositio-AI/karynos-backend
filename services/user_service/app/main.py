from fastapi import FastAPI
from api.main_router import router as main_router
from core.config import settings

app = FastAPI(title = settings.SERVICE_NAME)

app.include_router(main_router)