"""
Dream Action サービス

授業資料 + 生徒の仮の夢 → LLM → 補助教材 の生成パイプラインを担当する。
非同期処理は FastAPI BackgroundTasks で行い、GenerationJob テーブルで進捗を管理する。
"""

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException, status

from app.gateways.dream_action_gateway import dream_action_gateway
from app.gateways.mentor_gateway import mentor_gateway
from app.gateways.job_gateway import job_gateway
from app.services.dream_action.schemas import (
    DistributeMaterialRequest,
    DistributeMaterialResponse,
    GeneratedMaterialDetail,
    GeneratedMaterialListResponse,
    GeneratedMaterialSummary,
    GenerationJobListResponse,
    GenerationJobResponse,
    ModerationResult,
    TriggerGenerationRequest,
    TriggerGenerationResponse,
)
from app.utils.prompt_loader import load_prompt
from settings import settings

logger = logging.getLogger(__name__)


class DreamActionService:

    # ── 生成トリガー ──────────────────────────────────────────────────

    def trigger_generation(
        self,
        class_id: str,
        request: TriggerGenerationRequest,
        mentor_id: str,
        background_tasks: BackgroundTasks,
    ) -> TriggerGenerationResponse:
        """補助教材の生成ジョブを作成し、バックグラウンドで実行を開始する。"""
        self._require_class(class_id, mentor_id)

        # 授業資料の存在とクラス帰属を確認
        mat_result = mentor_gateway.get_material(str(request.lesson_material_id))
        if not mat_result["success"] or not mat_result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="授業資料が見つかりません")
        material = mat_result["data"][0]
        if str(material.class_id) != class_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この授業資料はこのクラスに属していません")

        job_result = dream_action_gateway.create_generation_job({
            "lesson_material_id": str(request.lesson_material_id),
            "class_id": class_id,
            "status": "PENDING",
        })
        if not job_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="生成ジョブの作成に失敗しました",
            )

        job = job_result["data"]
        generation_job_id = str(job.generation_job_id)

        background_tasks.add_task(
            self._run_generation_job,
            generation_job_id=generation_job_id,
            lesson_material_id=str(request.lesson_material_id),
            class_id=class_id,
            target_dreamer_ids=(
                [str(d) for d in request.target_dreamer_ids]
                if request.target_dreamer_ids else None
            ),
            force_regenerate=request.force_regenerate,
        )

        return TriggerGenerationResponse(
            generation_job_id=UUID(generation_job_id),
            status="PENDING",
            message="補助教材の生成を開始しました",
        )

    # ── バックグラウンド生成パイプライン ──────────────────────────────

    def _run_generation_job(
        self,
        generation_job_id: str,
        lesson_material_id: str,
        class_id: str,
        target_dreamer_ids: list[str] | None,
        force_regenerate: bool,
    ) -> None:
        """生成ジョブのメインループ。BackgroundTask として実行される。"""
        logger.info("生成ジョブ開始: %s", generation_job_id)

        dream_action_gateway.update_generation_job(
            generation_job_id,
            {
                "status": "PROCESSING",
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        try:
            mat_result = mentor_gateway.get_material(lesson_material_id)
            if not mat_result["success"] or not mat_result["data"]:
                raise ValueError("授業資料が見つかりません")
            material = mat_result["data"][0]

            if target_dreamer_ids:
                dreamer_ids = target_dreamer_ids
            else:
                enr_result = mentor_gateway.list_enrollments(class_id)
                if not enr_result["success"]:
                    raise ValueError("履修生徒の取得に失敗しました")
                dreamer_ids = [str(e.dreamer_id) for e in (enr_result["data"] or [])]

            total = len(dreamer_ids)
            dream_action_gateway.update_generation_job(
                generation_job_id, {"total_dreamers": total}
            )

            completed = 0
            for dreamer_id in dreamer_ids:
                try:
                    self._generate_for_dreamer(
                        dreamer_id=dreamer_id,
                        material=material,
                        force_regenerate=force_regenerate,
                    )
                except Exception as exc:
                    logger.warning("dreamer %s の生成に失敗: %s", dreamer_id, exc)

                completed += 1
                progress = int(completed / total * 100) if total > 0 else 100
                dream_action_gateway.update_generation_job(
                    generation_job_id,
                    {"completed_dreamers": completed, "progress": progress},
                )

            dream_action_gateway.update_generation_job(
                generation_job_id,
                {
                    "status": "COMPLETED",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress": 100,
                },
            )
            logger.info("生成ジョブ完了: %s", generation_job_id)

        except Exception as exc:
            logger.error("生成ジョブ失敗: %s - %s", generation_job_id, exc)
            dream_action_gateway.update_generation_job(
                generation_job_id,
                {
                    "status": "FAILED",
                    "error_message": str(exc)[:500],
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
            )

    def _generate_for_dreamer(
        self, dreamer_id: str, material, force_regenerate: bool
    ) -> None:
        """1 人の生徒に対して補助教材を生成・保存する。"""
        lesson_material_id = str(material.material_id)
        idempotency_key = f"{lesson_material_id}:{dreamer_id}"

        existing = dream_action_gateway.get_generated_material_by_idempotency(idempotency_key)
        existing_id: str | None = None
        if existing["success"] and existing["data"]:
            if not force_regenerate:
                return
            existing_id = str(existing["data"][0].generated_material_id)

        from app.gateways.dreamer_gateway import dreamer_gateway

        dreamer_result = dreamer_gateway.get_dreamer(dreamer_id)
        if not dreamer_result["success"] or not dreamer_result["data"]:
            raise ValueError(f"生徒 {dreamer_id} が見つかりません")
        dreamer = dreamer_result["data"][0]

        # 仮の夢（最も最近 good したジョブ）を取得
        history_result = job_gateway.get_history(UUID(dreamer_id))
        liked_histories = []
        if history_result.get("success") and history_result.get("data"):
            liked_histories = [
                h for h in history_result["data"] if getattr(h, "good", False)
            ]

        if not liked_histories:
            logger.info("生徒 %s にはいいね済みの職業がないのでスキップ", dreamer_id)
            return

        latest_liked = liked_histories[-1]
        job_id = int(getattr(latest_liked, "job_id", 0))

        job_resp = job_gateway.get_job(job_id)
        if not job_resp.get("success") or not job_resp.get("data"):
            raise ValueError(f"職業 {job_id} が見つかりません")
        job = job_resp["data"][0]

        lesson_content = (material.content_text or "")[:3000]
        student_name = f"{dreamer.name_family} {dreamer.name_given}"
        job_name = job.name
        job_description = (job.description or "")[:500]

        prompt = load_prompt(
            "dream_action/generate_material.txt",
            student_name=student_name,
            job_name=job_name,
            job_description=job_description,
            subject=material.subject or "未設定",
            unit=material.unit or "未設定",
            material_title=material.title,
            lesson_content=(
                lesson_content if lesson_content
                else "（授業資料のテキストが取得できませんでした）"
            ),
        )

        generated_content = self._call_llm(prompt)

        mod_result = self._moderate_content(generated_content)
        if not mod_result.is_safe:
            logger.warning(
                "モデレーション不合格 dreamer=%s reason=%s", dreamer_id, mod_result.reason
            )
            return

        title = f"{job_name} を目指す {student_name} さんへ（{material.title}）"

        if existing_id:
            dream_action_gateway.update_generated_material(
                existing_id,
                {
                    "content": generated_content,
                    "title": title,
                    "status": "DRAFT",
                    "is_read": False,
                    "distributed_at": None,
                },
            )
        else:
            result = dream_action_gateway.create_generated_material({
                "lesson_material_id": lesson_material_id,
                "dreamer_id": dreamer_id,
                "job_id": job_id,
                "job_name": job_name,
                "title": title,
                "content": generated_content,
                "status": "DRAFT",
                "idempotency_key": idempotency_key,
            })
            if not result["success"]:
                raise ValueError(f"教材の保存に失敗: {result.get('message')}")

    def _call_llm(self, prompt: str) -> str:
        """OpenAI Chat Completions を同期呼び出しする。"""
        import os

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY 未設定 — モックコンテンツを返します")
            return (
                "# サンプル補助教材\n\n"
                "（OPENAI_API_KEY が未設定のためサンプルです）\n\n"
                "## この授業が将来どう活きるか\n\nサンプルテキスト。\n"
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.DREAM_ACTION_MAX_TOKENS,
                temperature=0.7,
                timeout=settings.DREAM_ACTION_TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("LLM 呼び出し失敗: %s", exc)
            raise ValueError(f"LLM 呼び出しに失敗しました: {exc}") from exc

    def _moderate_content(self, content: str) -> ModerationResult:
        """生成コンテンツの適切性チェックを行う。"""
        import os

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return ModerationResult(is_safe=True, reason="")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            prompt = load_prompt("dream_action/moderation_check.txt", content=content)
            response = client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0,
                timeout=30,
            )
            raw = (response.choices[0].message.content or "{}").strip()
            try:
                data = json.loads(raw)
                return ModerationResult(
                    is_safe=bool(data.get("is_safe", True)),
                    reason=data.get("reason", ""),
                )
            except json.JSONDecodeError:
                logger.warning("モデレーションレスポンスのパース失敗: %s", raw[:200])
                return ModerationResult(is_safe=True, reason="")
        except Exception as exc:
            logger.warning("モデレーションチェック失敗（スキップ）: %s", exc)
            return ModerationResult(is_safe=True, reason="")

    # ── GenerationJob 参照 ────────────────────────────────────────────

    def get_generation_job(
        self, generation_job_id: str, class_id: str, mentor_id: str
    ) -> GenerationJobResponse:
        self._require_class(class_id, mentor_id)
        result = dream_action_gateway.get_generation_job(generation_job_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="生成ジョブが見つかりません")
        job = result["data"][0]
        if str(job.class_id) != class_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="このジョブにはアクセスできません")
        return GenerationJobResponse.model_validate(job)

    def list_generation_jobs(
        self, class_id: str, mentor_id: str
    ) -> GenerationJobListResponse:
        self._require_class(class_id, mentor_id)
        result = dream_action_gateway.list_generation_jobs_by_class(class_id)
        items = []
        if result["success"] and result["data"]:
            items = [GenerationJobResponse.model_validate(j) for j in result["data"]]
        return GenerationJobListResponse(items=items, total=len(items))

    # ── GeneratedMaterial (Mentor 向け) ───────────────────────────────

    def list_generated_materials(
        self,
        class_id: str,
        mentor_id: str,
        lesson_material_id: str | None = None,
        status_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> GeneratedMaterialListResponse:
        self._require_class(class_id, mentor_id)

        if lesson_material_id:
            result = dream_action_gateway.list_generated_materials_by_lesson(lesson_material_id)
        else:
            result = dream_action_gateway.list_generated_materials_by_class(class_id)

        all_items = result["data"] if result["success"] else []
        if status_filter:
            all_items = [
                m for m in (all_items or [])
                if getattr(m, "status", "") == status_filter
            ]

        paged = (all_items or [])[offset : offset + limit]
        return GeneratedMaterialListResponse(
            items=[GeneratedMaterialSummary.model_validate(m) for m in paged],
            total=len(all_items or []),
        )

    def get_generated_material_detail(
        self, class_id: str, generated_material_id: str, mentor_id: str
    ) -> GeneratedMaterialDetail:
        self._require_class(class_id, mentor_id)
        result = dream_action_gateway.get_generated_material(generated_material_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="補助教材が見つかりません")
        mat = result["data"][0]
        # 授業資料がこのクラスに属しているか確認
        mat_result = mentor_gateway.get_material(str(mat.lesson_material_id))
        if mat_result["success"] and mat_result["data"]:
            if str(mat_result["data"][0].class_id) != class_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="この教材にはアクセスできません"
                )
        return GeneratedMaterialDetail.model_validate(mat)

    def distribute_materials(
        self, class_id: str, request: DistributeMaterialRequest, mentor_id: str
    ) -> DistributeMaterialResponse:
        self._require_class(class_id, mentor_id)

        distributed_count = 0
        now = datetime.now(timezone.utc).isoformat()
        for mat_id in request.generated_material_ids:
            result = dream_action_gateway.update_generated_material(
                str(mat_id),
                {"status": "DISTRIBUTED", "distributed_at": now},
            )
            if result["success"]:
                distributed_count += 1

        return DistributeMaterialResponse(
            distributed_count=distributed_count,
            message=f"{distributed_count} 件の教材を配布しました",
        )

    def regenerate_material(
        self,
        class_id: str,
        generated_material_id: str,
        mentor_id: str,
        background_tasks: BackgroundTasks,
    ) -> TriggerGenerationResponse:
        """指定した補助教材を再生成する。"""
        self._require_class(class_id, mentor_id)

        result = dream_action_gateway.get_generated_material(generated_material_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="補助教材が見つかりません")
        mat = result["data"][0]

        # 授業資料の帰属確認
        mat_result = mentor_gateway.get_material(str(mat.lesson_material_id))
        if not mat_result["success"] or not mat_result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="授業資料が見つかりません")
        if str(mat_result["data"][0].class_id) != class_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この教材にはアクセスできません")

        job_result = dream_action_gateway.create_generation_job({
            "lesson_material_id": str(mat.lesson_material_id),
            "class_id": class_id,
            "status": "PENDING",
        })
        if not job_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="再生成ジョブの作成に失敗しました",
            )

        job = job_result["data"]
        generation_job_id = str(job.generation_job_id)

        background_tasks.add_task(
            self._run_generation_job,
            generation_job_id=generation_job_id,
            lesson_material_id=str(mat.lesson_material_id),
            class_id=class_id,
            target_dreamer_ids=[str(mat.dreamer_id)],
            force_regenerate=True,
        )

        return TriggerGenerationResponse(
            generation_job_id=UUID(generation_job_id),
            status="PENDING",
            message="補助教材の再生成を開始しました",
        )

    # ── GeneratedMaterial (Dreamer 向け) ──────────────────────────────

    def list_materials_for_dreamer(
        self, dreamer_id: str, limit: int = 50, offset: int = 0
    ) -> GeneratedMaterialListResponse:
        result = dream_action_gateway.list_generated_materials_by_dreamer(dreamer_id)
        all_items = []
        if result["success"] and result["data"]:
            all_items = [
                m for m in result["data"]
                if getattr(m, "status", "") == "DISTRIBUTED"
            ]

        paged = all_items[offset : offset + limit]
        return GeneratedMaterialListResponse(
            items=[GeneratedMaterialSummary.model_validate(m) for m in paged],
            total=len(all_items),
        )

    def get_material_for_dreamer(
        self, dreamer_id: str, generated_material_id: str
    ) -> GeneratedMaterialDetail:
        result = dream_action_gateway.get_generated_material(generated_material_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="補助教材が見つかりません")
        mat = result["data"][0]

        if str(mat.dreamer_id) != dreamer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="この教材にはアクセスできません"
            )
        if getattr(mat, "status", "") != "DISTRIBUTED":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="この教材はまだ配布されていません"
            )

        return GeneratedMaterialDetail.model_validate(mat)

    def mark_as_read(self, dreamer_id: str, generated_material_id: str) -> dict:
        result = dream_action_gateway.get_generated_material(generated_material_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="補助教材が見つかりません")
        mat = result["data"][0]

        if str(mat.dreamer_id) != dreamer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="この教材にはアクセスできません"
            )

        dream_action_gateway.update_generated_material(
            generated_material_id, {"is_read": True}
        )
        return {"message": "既読にしました"}

    # ── ヘルパー ──────────────────────────────────────────────────────

    def _require_class(self, class_id: str, mentor_id: str):
        result = mentor_gateway.get_class(class_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="クラスが見つかりません")
        cls = result["data"][0]
        if str(cls.mentor_id) != mentor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="このクラスにはアクセスできません"
            )
        return cls


dream_action_service = DreamActionService()
