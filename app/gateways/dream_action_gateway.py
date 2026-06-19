from typing import Any

from app.gateways.db.base_prisma_gateway import BasePrismaGateway
from app.gateways.result import GatewayResult


class DreamActionGateway(BasePrismaGateway):
    GEN_MATERIAL = "generatedmaterial"
    GEN_JOB = "generationjob"

    # ── GeneratedMaterial ─────────────────────────────────────────────

    def get_generated_material(self, generated_material_id: str) -> GatewayResult:
        return self.find_many(
            self.GEN_MATERIAL,
            {"generated_material_id": generated_material_id},
        )

    def list_generated_materials_by_dreamer(self, dreamer_id: str) -> GatewayResult:
        return self.find_many(self.GEN_MATERIAL, {"dreamer_id": dreamer_id})

    def list_generated_materials_by_lesson(self, lesson_material_id: str) -> GatewayResult:
        return self.find_many(
            self.GEN_MATERIAL, {"lesson_material_id": lesson_material_id}
        )

    def list_generated_materials_by_class(self, class_id: str) -> GatewayResult:
        """クラスに紐づく全生成教材を返す（lesson_material 経由の間接参照は Gateway 外で行う）。"""
        from app.gateways.mentor_gateway import mentor_gateway

        mats_result = mentor_gateway.list_materials(class_id)
        if not mats_result["success"] or not mats_result["data"]:
            return {"success": True, "message": ["Success"], "data": []}

        all_gen: list[Any] = []
        for mat in mats_result["data"]:
            result = self.list_generated_materials_by_lesson(str(mat.material_id))
            if result["success"] and result["data"]:
                all_gen.extend(result["data"])

        return {"success": True, "message": ["Success"], "data": all_gen}

    def get_generated_material_by_idempotency(
        self, idempotency_key: str
    ) -> GatewayResult:
        return self.find_many(
            self.GEN_MATERIAL, {"idempotency_key": idempotency_key}
        )

    def create_generated_material(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.GEN_MATERIAL, payload)

    def update_generated_material(
        self, generated_material_id: str, payload: dict[str, Any]
    ) -> GatewayResult:
        return self.update_many_and_fetch(
            self.GEN_MATERIAL,
            {"generated_material_id": generated_material_id},
            payload,
        )

    # ── GenerationJob ─────────────────────────────────────────────────

    def create_generation_job(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.GEN_JOB, payload)

    def get_generation_job(self, generation_job_id: str) -> GatewayResult:
        return self.find_many(
            self.GEN_JOB, {"generation_job_id": generation_job_id}
        )

    def list_generation_jobs_by_class(self, class_id: str) -> GatewayResult:
        return self.find_many(self.GEN_JOB, {"class_id": class_id})

    def list_generation_jobs_by_material(self, lesson_material_id: str) -> GatewayResult:
        return self.find_many(
            self.GEN_JOB, {"lesson_material_id": lesson_material_id}
        )

    def update_generation_job(
        self, generation_job_id: str, payload: dict[str, Any]
    ) -> GatewayResult:
        return self.update_many_and_fetch(
            self.GEN_JOB,
            {"generation_job_id": generation_job_id},
            payload,
        )


dream_action_gateway = DreamActionGateway()
