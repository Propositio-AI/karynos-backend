import asyncio
import os
import platform
import struct
import threading
from pathlib import Path
from typing import Any

from fastapi.encoders import jsonable_encoder

from app.gateways.result import GatewayResult
from app.gen.prisma import Prisma

_client = Prisma()
_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None
_loop_lock = threading.Lock()


def _ensure_loop() -> asyncio.AbstractEventLoop:
    global _loop, _loop_thread

    if _loop is not None:
        return _loop

    with _loop_lock:
        if _loop is not None:
            return _loop

        ready = threading.Event()

        def _run_loop() -> None:
            global _loop
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            ready.set()
            _loop.run_forever()

        _loop_thread = threading.Thread(
            target=_run_loop, daemon=True, name="prisma-loop"
        )
        _loop_thread.start()
        ready.wait()
        return _loop  # type: ignore[return-value]


async def _ensure_connected() -> None:
    _maybe_set_prisma_query_engine_binary()
    if not _client.is_connected():
        await _client.connect()


_ELF_MACHINE_FOR_ARCH = {
    "aarch64": 0xB7,  # EM_AARCH64
    "x86_64": 0x3E,  # EM_X86_64
}


def _is_compatible_elf(path: Path) -> bool:
    """ELF バイナリが現在の CPU アーキテクチャと一致するか確認する。"""
    expected = _ELF_MACHINE_FOR_ARCH.get(platform.machine())
    if expected is None:
        return True
    try:
        with open(path, "rb") as f:
            if f.read(4) != b"\x7fELF":
                return True
            f.seek(18)
            (e_machine,) = struct.unpack_from("<H", f.read(2))
        return e_machine == expected
    except Exception:
        return True


def _maybe_set_prisma_query_engine_binary() -> None:
    if os.environ.get("PRISMA_QUERY_ENGINE_BINARY"):
        return

    cache_root = Path.home() / ".cache" / "prisma-python" / "binaries"
    if not cache_root.exists():
        return

    candidates = sorted(
        [
            *cache_root.glob("*/*/prisma-query-engine-linux-arm64-openssl-*"),
            *cache_root.glob("*/*/prisma-query-engine-debian-openssl-*"),
        ],
        reverse=True,
    )
    for candidate in candidates:
        if (
            candidate.is_file()
            and os.access(candidate, os.X_OK)
            and _is_compatible_elf(candidate)
        ):
            os.environ["PRISMA_QUERY_ENGINE_BINARY"] = str(candidate)
            return


def run_prisma(coro: Any) -> Any:
    loop = _ensure_loop()
    try:
        run_coroutine = asyncio.run_coroutine_threadsafe(_ensure_connected(), loop)
        run_coroutine.result()
    except Exception:
        close = getattr(coro, "close", None)
        if callable(close):
            close()
        raise

    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


def prisma_result(coro: Any) -> GatewayResult[Any]:
    try:
        return {
            "success": True,
            "message": ["Success"],
            "data": run_prisma(coro),
        }
    except Exception as exc:
        return {
            "success": False,
            "message": [str(exc)],
            "data": None,
        }


def payload_to_dict(payload: Any) -> dict[str, Any]:
    if payload is None:
        return {}
    if hasattr(payload, "model_dump"):
        return jsonable_encoder(payload.model_dump(exclude_none=True))
    if hasattr(payload, "dict"):
        return jsonable_encoder(payload.dict(exclude_none=True))
    if isinstance(payload, dict):
        return jsonable_encoder(payload)
    return jsonable_encoder(
        {
            key: value
            for key, value in vars(payload).items()
            if not key.startswith("_") and value is not None
        }
    )


def build_where(filters: list[list[Any]]) -> dict[str, Any]:
    where: dict[str, Any] = {}
    for column, operator, value in filters:
        if operator == "==":
            where[column] = value
        elif operator == "!=":
            where[column] = {"not": value}
        elif operator == ">":
            where[column] = {"gt": value}
        elif operator == "<":
            where[column] = {"lt": value}
        elif operator == ">=":
            where[column] = {"gte": value}
        elif operator == "<=":
            where[column] = {"lte": value}
        elif operator == "in":
            where[column] = {"in": value if isinstance(value, list) else [value]}
        elif operator in {"like", "ilike"}:
            text = str(value)
            text = text.strip("%")
            where[column] = {"contains": text}
            if operator == "ilike":
                where[column]["mode"] = "insensitive"
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    return where


def prisma_client() -> Prisma:
    return _client
