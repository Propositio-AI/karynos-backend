from uuid import UUID

TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user_id() -> UUID:
    return TEMP_USER_ID


async def get_current_user_id_str() -> str:
    return str(TEMP_USER_ID)
