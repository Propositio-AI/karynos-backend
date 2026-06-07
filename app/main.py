from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router.chats import router as chat_router
from app.router.dreamers import router as dreamer_router
from app.router.jobs import router as job_router
from settings import settings

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router)
app.include_router(dreamer_router)
app.include_router(chat_router)
