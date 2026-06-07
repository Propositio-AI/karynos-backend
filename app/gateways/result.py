from typing import Generic, TypeVar, TypedDict

T = TypeVar("T")


class GatewayResult(TypedDict, Generic[T]):
    success: bool
    message: list[str]
    data: T | None
