from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.main_router import router as main_router
from core.config import settings
from core import db
# from core.init_db import init_archive_type_table, init_archive_share_type_table

# init_archive_type_table()
# init_archive_share_type_table()

app = FastAPI(title = settings.SERVICE_NAME)

origins = [
    "http://localhost:3000",  # dev用
    # "https://your-app.com",  # prod用
]

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],       # ← OPTIONS 含めた全メソッド許可
    allow_headers=["*"],       # ← Content-Type など含め全て許可
)

app.include_router(main_router)