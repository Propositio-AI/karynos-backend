from typing import Any

from app.gateways.db.base_prisma_gateway import BasePrismaGateway
from app.gateways.result import GatewayResult


class MentorGateway(BasePrismaGateway):
    MENTOR = "mentor"
    CLASS = "schoolclass"
    ENROLLMENT = "enrollment"
    LESSON_MATERIAL = "lessonmaterial"

    # ── Mentor ────────────────────────────────────────────────────────

    def get_mentor_by_sub(self, cognito_sub: str) -> GatewayResult:
        return self.find_many(self.MENTOR, {"cognito_sub": cognito_sub})

    def get_mentor_by_id(self, mentor_id: str) -> GatewayResult:
        return self.find_many(self.MENTOR, {"mentor_id": mentor_id})

    def create_mentor(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.MENTOR, payload)

    def update_mentor(self, mentor_id: str, payload: dict[str, Any]) -> GatewayResult:
        return self.update_many_and_fetch(
            self.MENTOR, {"mentor_id": mentor_id}, payload
        )

    # ── Class ─────────────────────────────────────────────────────────

    def list_classes(self, mentor_id: str) -> GatewayResult:
        return self.find_many(self.CLASS, {"mentor_id": mentor_id})

    def get_class(self, class_id: str) -> GatewayResult:
        return self.find_many(self.CLASS, {"class_id": class_id})

    def create_class(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.CLASS, payload)

    def update_class(self, class_id: str, payload: dict[str, Any]) -> GatewayResult:
        return self.update_many_and_fetch(self.CLASS, {"class_id": class_id}, payload)

    def delete_class(self, class_id: str) -> GatewayResult:
        return self.delete_many_and_return_before(self.CLASS, {"class_id": class_id})

    # ── Enrollment ────────────────────────────────────────────────────

    def list_enrollments(self, class_id: str) -> GatewayResult:
        return self.find_many(self.ENROLLMENT, {"class_id": class_id})

    def get_enrollment(self, class_id: str, dreamer_id: str) -> GatewayResult:
        return self.find_many(
            self.ENROLLMENT, {"class_id": class_id, "dreamer_id": dreamer_id}
        )

    def create_enrollment(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.ENROLLMENT, payload)

    def delete_enrollment(self, class_id: str, dreamer_id: str) -> GatewayResult:
        return self.delete_many_and_return_before(
            self.ENROLLMENT, {"class_id": class_id, "dreamer_id": dreamer_id}
        )

    def count_enrollments(self, class_id: str) -> int:
        result = self.find_many(self.ENROLLMENT, {"class_id": class_id})
        if result["success"] and result["data"]:
            return len(result["data"])
        return 0

    # ── LessonMaterial ────────────────────────────────────────────────

    def list_materials(self, class_id: str) -> GatewayResult:
        return self.find_many(
            self.LESSON_MATERIAL, {"class_id": class_id, "is_deleted": False}
        )

    def get_material(self, material_id: str) -> GatewayResult:
        return self.find_many(
            self.LESSON_MATERIAL, {"material_id": material_id, "is_deleted": False}
        )

    def create_material(self, payload: dict[str, Any]) -> GatewayResult:
        return self.create(self.LESSON_MATERIAL, payload)

    def update_material(self, material_id: str, payload: dict[str, Any]) -> GatewayResult:
        return self.update_many_and_fetch(
            self.LESSON_MATERIAL, {"material_id": material_id}, payload
        )

    def soft_delete_material(self, material_id: str) -> GatewayResult:
        return self.update_many_and_fetch(
            self.LESSON_MATERIAL, {"material_id": material_id}, {"is_deleted": True}
        )

    def count_materials(self, class_id: str) -> int:
        result = self.find_many(
            self.LESSON_MATERIAL, {"class_id": class_id, "is_deleted": False}
        )
        if result["success"] and result["data"]:
            return len(result["data"])
        return 0


mentor_gateway = MentorGateway()
