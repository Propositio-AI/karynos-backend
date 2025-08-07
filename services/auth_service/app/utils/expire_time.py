from datetime import timedelta

from shared.utils.time import get_utc_time
from core.config import settings

def default_expires_at():
    return get_utc_time() + timedelta(minutes=settings.TOKEN_TOKEN_EXPIRES_MINUTES)