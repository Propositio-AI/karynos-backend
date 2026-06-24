from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from app.router.chats import router as chat_router
from app.router.dreamers import router as dreamer_router
from app.router.jobs import router as job_router
from app.router.matching import router as matching_router
from app.router.onboarding import router as onboarding_router
from settings import settings

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

v1 = APIRouter(prefix="/api/v1")
v1.include_router(chat_router, prefix="/chat", tags=["Chat"])
v1.include_router(dreamer_router, prefix="/dreamer", tags=["Dreamer"])
v1.include_router(job_router, prefix="/job", tags=["Job"])
v1.include_router(onboarding_router, prefix="/onboarding", tags=["Onboarding"])
v1.include_router(matching_router, prefix="/matching", tags=["Matching"])

app.include_router(v1)
