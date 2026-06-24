from typing import TypedDict


class GatewayResult[T](TypedDict):
    success: bool
    message: list[str]
    data: T | None
