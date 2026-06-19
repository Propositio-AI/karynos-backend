from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.router.chats import router as chat_router
from app.router.dream_action import router as dream_action_router
from app.router.dreamers import router as dreamer_router
from app.router.jobs import router as job_router
from app.router.matching import router as matching_router
from app.router.mentor import router as mentor_router
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

# ── 統一エラーレスポンス形式 ──────────────────────────────────────────────
# 全エラーは {"error": {"code": "...", "message": "...", "detail": ...}} 形式で返す

_HTTP_STATUS_TO_CODE = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def _error_response(status_code: int, message: str, detail=None) -> JSONResponse:
    code = _HTTP_STATUS_TO_CODE.get(status_code, "ERROR")
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "detail": detail}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return _error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "リクエストのバリデーションに失敗しました",
        detail=exc.errors(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "予期しないエラーが発生しました",
    )


# ── ルーター登録 ──────────────────────────────────────────────────────────

v1 = APIRouter(prefix="/api/v1")
v1.include_router(chat_router, prefix="/chat", tags=["Chat"])
v1.include_router(dreamer_router, prefix="/dreamer", tags=["Dreamer"])
v1.include_router(job_router, prefix="/job", tags=["Job"])
v1.include_router(onboarding_router, prefix="/onboarding", tags=["Onboarding"])
v1.include_router(matching_router, prefix="/matching", tags=["Matching"])
v1.include_router(mentor_router, prefix="/mentor", tags=["Mentor"])
v1.include_router(dream_action_router, prefix="/dream-action", tags=["Dream Action"])

app.include_router(v1)
