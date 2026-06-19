"""
Cognito JWT 認証・認可モジュール

- JWT の署名検証: Cognito JWKS エンドポイントから公開鍵を取得して検証する
- ロール判定: JWT の `cognito:groups` クレームで Dreamer / Mentor を区別する
- 開発用フォールバック: COGNITO_USER_POOL_ID が未設定の場合はモック認証に切り替わる
"""

import json
import logging
import time
from functools import lru_cache
from typing import Literal
from uuid import UUID

import urllib.request
from base64 import b64decode, urlsafe_b64decode

from fastapi import Depends, Header, HTTPException, status

from settings import settings

logger = logging.getLogger(__name__)

# ── モック用固定 ID（開発環境で Cognito 未設定時に使用）──────────────
_MOCK_DREAMER_ID = UUID("00000000-0000-0000-0000-000000000001")
_MOCK_MENTOR_ID = "00000000-0000-0000-0000-000000000002"
_MOCK_COGNITO_SUB_DREAMER = "mock-dreamer-sub"
_MOCK_COGNITO_SUB_MENTOR = "mock-mentor-sub"

Role = Literal["Dreamer", "Mentor"]


# ── JWKS キャッシュ ────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _fetch_jwks() -> dict:
    """Cognito JWKS を取得してキャッシュする（プロセス再起動まで保持）。"""
    try:
        with urllib.request.urlopen(settings.cognito_jwks_url, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        logger.warning("JWKS 取得失敗: %s", exc)
        return {"keys": []}


def _get_public_key(kid: str):
    """kid に対応する公開鍵オブジェクトを返す。cryptography ライブラリを使用する。"""
    try:
        from cryptography.hazmat.primitives.asymmetric.rsa import (
            RSAPublicNumbers,
        )
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cryptography パッケージが必要です: pip install cryptography",
        )

    jwks = _fetch_jwks()
    key_data = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key_data:
        _fetch_jwks.cache_clear()
        jwks = _fetch_jwks()
        key_data = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT 署名鍵が見つかりません",
        )

    def _b64_to_int(s: str) -> int:
        padding = "=" * (4 - len(s) % 4)
        return int.from_bytes(urlsafe_b64decode(s + padding), "big")

    n = _b64_to_int(key_data["n"])
    e = _b64_to_int(key_data["e"])
    return RSAPublicNumbers(e, n).public_key(default_backend())


def _decode_jwt_payload(token: str) -> dict:
    """JWT を署名検証なしでペイロードだけデコードする（事前チェック用）。"""
    try:
        parts = token.split(".")
        payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(urlsafe_b64decode(payload_b64))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT の形式が不正です",
        )


def _decode_jwt_header(token: str) -> dict:
    try:
        parts = token.split(".")
        header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
        return json.loads(urlsafe_b64decode(header_b64))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT ヘッダーの形式が不正です",
        )


def verify_jwt(token: str) -> dict:
    """
    Cognito JWT を完全に検証してペイロードを返す。

    検証内容:
    - RS256 署名（JWKS から公開鍵を取得）
    - iss（Cognito User Pool エンドポイントと一致するか）
    - aud または client_id（COGNITO_CLIENT_ID と一致するか）
    - exp（有効期限）
    """
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        import base64
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cryptography パッケージが必要です",
        )

    header = _decode_jwt_header(token)
    if header.get("alg") != "RS256":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT アルゴリズムが RS256 ではありません",
        )

    kid = header.get("kid", "")
    public_key = _get_public_key(kid)

    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT の形式が不正です",
        )

    message = f"{parts[0]}.{parts[1]}".encode("utf-8")
    sig_b64 = parts[2] + "=" * (4 - len(parts[2]) % 4)
    signature = urlsafe_b64decode(sig_b64)

    try:
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT 署名の検証に失敗しました",
        )

    payload = _decode_jwt_payload(token)

    if payload.get("iss") != settings.cognito_issuer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT の issuer が不正です",
        )

    if settings.COGNITO_CLIENT_ID:
        aud = payload.get("aud") or payload.get("client_id", "")
        if isinstance(aud, list):
            valid = settings.COGNITO_CLIENT_ID in aud
        else:
            valid = aud == settings.COGNITO_CLIENT_ID
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT の audience が不正です",
            )

    if payload.get("exp", 0) < time.time():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT の有効期限が切れています",
        )

    return payload


def _extract_token(authorization: str) -> str:
    """Authorization ヘッダーから Bearer トークンを取り出す。"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization ヘッダーが不正です（Bearer トークンが必要）",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization[7:].strip()


def _get_role_from_payload(payload: dict) -> Role:
    """JWT クレームからロールを返す。"""
    groups: list[str] = payload.get("cognito:groups") or []
    if "Mentor" in groups:
        return "Mentor"
    return "Dreamer"


# ── モード判定 ──────────────────────────────────────────────────────────

def _is_mock_mode() -> bool:
    """USE_MOCK_AUTH=True または COGNITO_USER_POOL_ID が未設定のときモックモードで動作する。"""
    return settings.USE_MOCK_AUTH or not settings.COGNITO_USER_POOL_ID


# ── 依存関係注入 ────────────────────────────────────────────────────────

async def get_current_user_id(
    authorization: str = Header(default=""),
) -> UUID:
    """現在の Dreamer の dreamer_id（UUID）を返す。モック時は固定値。"""
    if _is_mock_mode():
        return _MOCK_DREAMER_ID

    token = _extract_token(authorization)
    payload = verify_jwt(token)

    role = _get_role_from_payload(payload)
    if role != "Dreamer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作は Dreamer のみ実行できます",
        )

    sub = payload.get("sub", "")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT に sub クレームがありません",
        )

    from app.gateways.dreamer_gateway import dreamer_gateway

    result = dreamer_gateway.get_dreamer_by_sub(sub)
    if not result["success"] or not result["data"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証済みの Dreamer アカウントが見つかりません",
        )
    return UUID(str(result["data"][0].dreamer_id))


async def get_current_user_id_str(
    authorization: str = Header(default=""),
) -> str:
    uid = await get_current_user_id(authorization)
    return str(uid)


async def get_current_dreamer_sub(
    authorization: str = Header(default=""),
) -> str:
    """Dreamer の Cognito sub を返す。"""
    if _is_mock_mode():
        return _MOCK_COGNITO_SUB_DREAMER

    token = _extract_token(authorization)
    payload = verify_jwt(token)

    role = _get_role_from_payload(payload)
    if role != "Dreamer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作は Dreamer のみ実行できます",
        )

    return payload.get("sub", "")


async def get_current_mentor_sub(
    authorization: str = Header(default=""),
) -> str:
    """Mentor の Cognito sub を返す。"""
    if _is_mock_mode():
        return _MOCK_COGNITO_SUB_MENTOR

    token = _extract_token(authorization)
    payload = verify_jwt(token)

    role = _get_role_from_payload(payload)
    if role != "Mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作は Mentor のみ実行できます",
        )

    return payload.get("sub", "")


async def get_current_role(
    authorization: str = Header(default=""),
) -> Role:
    """現在のユーザーのロールを返す。"""
    if _is_mock_mode():
        return "Dreamer"

    token = _extract_token(authorization)
    payload = verify_jwt(token)
    return _get_role_from_payload(payload)
