"""
Dream Action サービスのユニットテスト。
DB・OpenAI はすべてモック。
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import os

import pytest

os.environ.setdefault("DB_USER", "karynos")
os.environ.setdefault("DB_PASS", "karynos")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "karynos")

sys.path.insert(0, str(Path(__file__).parent.parent))


def _make_class(class_id="cls-1", mentor_id="mentor-1"):
    return SimpleNamespace(class_id=class_id, mentor_id=mentor_id)


def _make_material(
    material_id="mat-1",
    class_id="cls-1",
    mentor_id="mentor-1",
    title="テスト授業",
    subject="数学",
    unit="因数分解",
    content_text="二次方程式の解法",
):
    return SimpleNamespace(
        material_id=material_id,
        class_id=class_id,
        mentor_id=mentor_id,
        title=title,
        subject=subject,
        unit=unit,
        content_text=content_text,
    )


def _make_dreamer(dreamer_id="d-1", name_family="山田", name_given="太郎"):
    return SimpleNamespace(
        dreamer_id=dreamer_id,
        name_family=name_family,
        name_given=name_given,
    )


def _make_job(job_id=1, name="エンジニア", description="システムを作る職業"):
    return SimpleNamespace(job_id=job_id, name=name, description=description)


def _ok(data):
    return {"success": True, "message": ["Success"], "data": data}


def _ng(msg="error"):
    return {"success": False, "message": [msg], "data": None}


class TestCallLlm:
    def test_returns_mock_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from app.services.dream_action.service import DreamActionService

        svc = DreamActionService()
        result = svc._call_llm("test prompt")
        assert "サンプル" in result

    def test_calls_openai_when_key_set(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "生成コンテンツ"

        with patch("openai.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.chat.completions.create.return_value = mock_response

            from app.services.dream_action.service import DreamActionService

            svc = DreamActionService()
            result = svc._call_llm("test prompt")
            assert result == "生成コンテンツ"


class TestModerateContent:
    def test_safe_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from app.services.dream_action.service import DreamActionService

        svc = DreamActionService()
        result = svc._moderate_content("some content")
        assert result.is_safe is True

    def test_parse_safe_response(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"is_safe": true, "reason": ""}'

        with patch("openai.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.chat.completions.create.return_value = mock_response
            with patch("app.utils.prompt_loader.load_prompt", return_value="prompt"):
                from app.services.dream_action.service import DreamActionService

                svc = DreamActionService()
                result = svc._moderate_content("safe content")
                assert result.is_safe is True

    def test_parse_unsafe_response(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            '{"is_safe": false, "reason": "暴力的な表現"}'
        )

        with patch("openai.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.chat.completions.create.return_value = mock_response
            with patch("app.utils.prompt_loader.load_prompt", return_value="prompt"):
                from app.services.dream_action.service import DreamActionService

                svc = DreamActionService()
                result = svc._moderate_content("unsafe content")
                assert result.is_safe is False
                assert "暴力的" in result.reason


class TestDistributeMaterials:
    def test_distribute_success(self):
        from app.services.dream_action.schemas import DistributeMaterialRequest
        from app.services.dream_action.service import DreamActionService
        from uuid import UUID

        svc = DreamActionService()

        mat_id = "00000000-0000-0000-0000-000000000099"
        class_id = "00000000-0000-0000-0000-000000000001"
        mentor_id = "00000000-0000-0000-0000-000000000002"

        cls = _make_class(class_id=class_id, mentor_id=mentor_id)

        with (
            patch(
                "app.gateways.mentor_gateway.MentorGateway.get_class",
                return_value=_ok([cls]),
            ),
            patch(
                "app.gateways.dream_action_gateway.DreamActionGateway.update_generated_material",
                return_value=_ok([]),
            ),
        ):
            request = DistributeMaterialRequest(
                generated_material_ids=[UUID(mat_id)]
            )
            result = svc.distribute_materials(class_id, request, mentor_id)
            assert result.distributed_count == 1

    def test_distribute_forbidden(self):
        from fastapi import HTTPException

        from app.services.dream_action.schemas import DistributeMaterialRequest
        from app.services.dream_action.service import DreamActionService
        from uuid import UUID

        svc = DreamActionService()
        class_id = "00000000-0000-0000-0000-000000000001"
        mentor_id = "00000000-0000-0000-0000-000000000002"
        other_mentor_id = "00000000-0000-0000-0000-000000000003"

        cls = _make_class(class_id=class_id, mentor_id=other_mentor_id)

        with patch(
            "app.gateways.mentor_gateway.MentorGateway.get_class",
            return_value=_ok([cls]),
        ):
            request = DistributeMaterialRequest(
                generated_material_ids=[UUID("00000000-0000-0000-0000-000000000099")]
            )
            with pytest.raises(HTTPException) as exc:
                svc.distribute_materials(class_id, request, mentor_id)
            assert exc.value.status_code == 403


class TestListMaterialsForDreamer:
    def test_only_distributed_returned(self):
        from app.services.dream_action.service import DreamActionService

        svc = DreamActionService()
        dreamer_id = "00000000-0000-0000-0000-000000000001"

        draft_mat = SimpleNamespace(
            generated_material_id="m1",
            lesson_material_id="lm1",
            dreamer_id=dreamer_id,
            job_id=1,
            job_name="医師",
            title="タイトル",
            status="DRAFT",
            is_read=False,
            distributed_at=None,
            created_at=None,
            updated_at=None,
        )
        dist_mat = SimpleNamespace(
            generated_material_id="m2",
            lesson_material_id="lm1",
            dreamer_id=dreamer_id,
            job_id=1,
            job_name="医師",
            title="タイトル",
            status="DISTRIBUTED",
            is_read=False,
            distributed_at=None,
            created_at=None,
            updated_at=None,
        )

        with patch(
            "app.gateways.dream_action_gateway.DreamActionGateway.list_generated_materials_by_dreamer",
            return_value=_ok([draft_mat, dist_mat]),
        ):
            result = svc.list_materials_for_dreamer(dreamer_id)
            assert result.total == 1
            assert result.items[0].status == "DISTRIBUTED"
