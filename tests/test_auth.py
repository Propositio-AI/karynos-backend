"""認証・認可ユーティリティのユニットテスト（モックモードで実行）。"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Cognito 未設定 → モックモードで動作することを前提とする
os.environ.setdefault("DB_USER", "karynos")
os.environ.setdefault("DB_PASS", "karynos")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "karynos")


def test_mock_mode_no_cognito_pool():
    from app.lib.auth import _is_mock_mode

    with patch("app.lib.auth.settings") as mock_settings:
        mock_settings.COGNITO_USER_POOL_ID = ""
        assert _is_mock_mode() is True


def test_mock_mode_with_cognito_pool():
    from app.lib.auth import _is_mock_mode

    with patch("app.lib.auth.settings") as mock_settings:
        mock_settings.COGNITO_USER_POOL_ID = "ap-northeast-1_XXXXXXXX"
        assert _is_mock_mode() is False


def test_get_role_dreamer():
    from app.lib.auth import _get_role_from_payload

    payload = {"sub": "abc", "cognito:groups": ["Dreamer"]}
    assert _get_role_from_payload(payload) == "Dreamer"


def test_get_role_mentor():
    from app.lib.auth import _get_role_from_payload

    payload = {"sub": "abc", "cognito:groups": ["Mentor"]}
    assert _get_role_from_payload(payload) == "Mentor"


def test_get_role_default_dreamer():
    """グループが設定されていない場合は Dreamer として扱う。"""
    from app.lib.auth import _get_role_from_payload

    payload = {"sub": "abc"}
    assert _get_role_from_payload(payload) == "Dreamer"


def test_extract_token_valid():
    from app.lib.auth import _extract_token

    token = _extract_token("Bearer mytoken123")
    assert token == "mytoken123"


def test_extract_token_invalid():
    from fastapi import HTTPException

    from app.lib.auth import _extract_token

    with pytest.raises(HTTPException) as exc_info:
        _extract_token("NotBearer token")
    assert exc_info.value.status_code == 401


def test_decode_jwt_payload_malformed():
    from fastapi import HTTPException

    from app.lib.auth import _decode_jwt_payload

    with pytest.raises(HTTPException):
        _decode_jwt_payload("not.a.jwt")
