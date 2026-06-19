"""Mentor サービスの認可チェックのユニットテスト。"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

os.environ.setdefault("DB_USER", "karynos")
os.environ.setdefault("DB_PASS", "karynos")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "karynos")

sys.path.insert(0, str(Path(__file__).parent.parent))


def _ok(data):
    return {"success": True, "message": ["Success"], "data": data}


def _ng(msg="error"):
    return {"success": False, "message": [msg], "data": None}


def _make_class(class_id="cls-1", mentor_id="mentor-1"):
    from datetime import datetime

    return SimpleNamespace(
        class_id=class_id,
        mentor_id=mentor_id,
        name="3年A組",
        subject="数学",
        description=None,
        academic_year=2025,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestGetClass:
    def test_get_class_success(self):
        from app.services.mentor.service import MentorService

        svc = MentorService()
        cls = _make_class(class_id="cls-1", mentor_id="mentor-1")

        with (
            patch(
                "app.gateways.mentor_gateway.MentorGateway.get_class",
                return_value=_ok([cls]),
            ),
            patch(
                "app.gateways.mentor_gateway.MentorGateway.count_enrollments",
                return_value=5,
            ),
            patch(
                "app.gateways.mentor_gateway.MentorGateway.count_materials",
                return_value=2,
            ),
        ):
            result = svc.get_class("cls-1", "mentor-1")
            assert str(result.class_id) == "cls-1"
            assert result.enrolled_count == 5

    def test_get_class_forbidden(self):
        from fastapi import HTTPException

        from app.services.mentor.service import MentorService

        svc = MentorService()
        cls = _make_class(class_id="cls-1", mentor_id="other-mentor")

        with patch(
            "app.gateways.mentor_gateway.MentorGateway.get_class",
            return_value=_ok([cls]),
        ):
            with pytest.raises(HTTPException) as exc:
                svc.get_class("cls-1", "mentor-1")
            assert exc.value.status_code == 403

    def test_get_class_not_found(self):
        from fastapi import HTTPException

        from app.services.mentor.service import MentorService

        svc = MentorService()

        with patch(
            "app.gateways.mentor_gateway.MentorGateway.get_class",
            return_value=_ok([]),
        ):
            with pytest.raises(HTTPException) as exc:
                svc.get_class("cls-999", "mentor-1")
            assert exc.value.status_code == 404


class TestDeleteClass:
    def test_delete_class_success(self):
        from app.services.mentor.service import MentorService

        svc = MentorService()
        cls = _make_class()

        with (
            patch(
                "app.gateways.mentor_gateway.MentorGateway.get_class",
                return_value=_ok([cls]),
            ),
            patch(
                "app.gateways.mentor_gateway.MentorGateway.delete_class",
                return_value=_ok([cls]),
            ),
        ):
            result = svc.delete_class("cls-1", "mentor-1")
            assert "削除" in result["message"]
