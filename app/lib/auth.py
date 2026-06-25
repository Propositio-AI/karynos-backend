from uuid import UUID

from fastapi import Header

TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user_id(
    x_dreamer_id: str | None = Header(default=None, alias="X-Dreamer-Id"),
) -> UUID:
    if x_dreamer_id:
        try:
            return UUID(x_dreamer_id)
        except ValueError:
            pass
    return TEMP_USER_ID


async def get_current_user_id_str(
    x_dreamer_id: str | None = Header(default=None, alias="X-Dreamer-Id"),
) -> str:
    return str(await get_current_user_id(x_dreamer_id))
