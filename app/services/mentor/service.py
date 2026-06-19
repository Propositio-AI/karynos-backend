from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.gateways import dreamer_gateway, job_gateway
from app.gateways.mentor_gateway import mentor_gateway
from app.services.mentor.schemas import (
    CategoryDistribution,
    ClassAnalyticsResponse,
    ClassCreateRequest,
    ClassListResponse,
    ClassResponse,
    ClassUpdateRequest,
    EnrollmentCreateRequest,
    EnrollmentResponse,
    JobInterestSummary,
    LessonMaterialListResponse,
    LessonMaterialResponse,
    LessonMaterialUpdateRequest,
    MentorCreateRequest,
    MentorResponse,
    StudentDetail,
    StudentListResponse,
    StudentSummary,
)
from app.utils.file_storage import (
    extract_text_from_upload,
    save_upload,
    validate_upload,
)

_MOCK_MENTOR_ID = "00000000-0000-0000-0000-000000000002"
_MOCK_COGNITO_SUB = "mock-mentor-sub"


class MentorService:
    # ── Mentor 解決 ────────────────────────────────────────────────────

    def get_or_create_mentor(self, cognito_sub: str, request: MentorCreateRequest | None = None):
        """Cognito sub から Mentor を取得。存在しない場合は作成する。"""
        result = mentor_gateway.get_mentor_by_sub(cognito_sub)
        if result["success"] and result["data"]:
            return result["data"][0]

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="メンターが見つかりません。先に登録が必要です。",
            )

        create_result = mentor_gateway.create_mentor(
            {
                "cognito_sub": cognito_sub,
                "login_id": cognito_sub,
                "name_family": request.name_family,
                "name_given": request.name_given,
                "email": request.email,
            }
        )
        self._ensure_success(create_result)
        return create_result["data"]

    def resolve_mentor_id(self, cognito_sub: str) -> str:
        """Cognito sub → mentor_id を解決する。モック時は固定値。"""
        if cognito_sub == _MOCK_COGNITO_SUB:
            return _MOCK_MENTOR_ID

        result = mentor_gateway.get_mentor_by_sub(cognito_sub)
        if not result["success"] or not result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="メンターが見つかりません",
            )
        return str(result["data"][0].mentor_id)

    def get_mentor(self, cognito_sub: str) -> MentorResponse:
        result = mentor_gateway.get_mentor_by_sub(cognito_sub)
        if not result["success"] or not result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="メンターが見つかりません",
            )
        return MentorResponse.model_validate(result["data"][0])

    # ── Class CRUD ─────────────────────────────────────────────────────

    def list_classes(self, mentor_id: str) -> ClassListResponse:
        result = mentor_gateway.list_classes(mentor_id)
        self._ensure_success(result)
        items = []
        for cls in result["data"] or []:
            items.append(
                ClassResponse(
                    class_id=cls.class_id,
                    mentor_id=cls.mentor_id,
                    name=cls.name,
                    subject=cls.subject,
                    description=cls.description,
                    academic_year=cls.academic_year,
                    created_at=cls.created_at,
                    updated_at=cls.updated_at,
                    enrolled_count=mentor_gateway.count_enrollments(str(cls.class_id)),
                    material_count=mentor_gateway.count_materials(str(cls.class_id)),
                )
            )
        return ClassListResponse(items=items, total=len(items))

    def get_class(self, class_id: str, mentor_id: str) -> ClassResponse:
        cls = self._require_class(class_id, mentor_id)
        return ClassResponse(
            class_id=cls.class_id,
            mentor_id=cls.mentor_id,
            name=cls.name,
            subject=cls.subject,
            description=cls.description,
            academic_year=cls.academic_year,
            created_at=cls.created_at,
            updated_at=cls.updated_at,
            enrolled_count=mentor_gateway.count_enrollments(class_id),
            material_count=mentor_gateway.count_materials(class_id),
        )

    def create_class(self, request: ClassCreateRequest, mentor_id: str) -> ClassResponse:
        result = mentor_gateway.create_class(
            {
                "mentor_id": mentor_id,
                "name": request.name,
                "subject": request.subject,
                "description": request.description,
                "academic_year": request.academic_year,
            }
        )
        self._ensure_success(result)
        cls = result["data"]
        return ClassResponse(
            class_id=cls.class_id,
            mentor_id=cls.mentor_id,
            name=cls.name,
            subject=cls.subject,
            description=cls.description,
            academic_year=cls.academic_year,
            created_at=cls.created_at,
            updated_at=cls.updated_at,
            enrolled_count=0,
            material_count=0,
        )

    def update_class(
        self, class_id: str, request: ClassUpdateRequest, mentor_id: str
    ) -> ClassResponse:
        self._require_class(class_id, mentor_id)
        payload = request.model_dump(exclude_none=True)
        result = mentor_gateway.update_class(class_id, payload)
        self._ensure_success(result)
        cls = result["data"][0]
        return ClassResponse(
            class_id=cls.class_id,
            mentor_id=cls.mentor_id,
            name=cls.name,
            subject=cls.subject,
            description=cls.description,
            academic_year=cls.academic_year,
            created_at=cls.created_at,
            updated_at=cls.updated_at,
            enrolled_count=mentor_gateway.count_enrollments(class_id),
            material_count=mentor_gateway.count_materials(class_id),
        )

    def delete_class(self, class_id: str, mentor_id: str) -> dict:
        self._require_class(class_id, mentor_id)
        result = mentor_gateway.delete_class(class_id)
        self._ensure_success(result)
        return {"message": "クラスを削除しました", "class_id": class_id}

    # ── Enrollment / Student ──────────────────────────────────────────

    def list_students(
        self, class_id: str, mentor_id: str, limit: int = 50, offset: int = 0
    ) -> StudentListResponse:
        self._require_class(class_id, mentor_id)
        enrollments_result = mentor_gateway.list_enrollments(class_id)
        self._ensure_success(enrollments_result)

        all_enrollments = enrollments_result["data"] or []
        paged = all_enrollments[offset : offset + limit]

        items = []
        for enrollment in paged:
            dreamer_result = dreamer_gateway.get_dreamer(str(enrollment.dreamer_id))
            if not dreamer_result["success"] or not dreamer_result["data"]:
                continue
            dreamer = dreamer_result["data"][0]
            items.append(
                StudentSummary(
                    dreamer_id=dreamer.dreamer_id,
                    name_family=dreamer.name_family,
                    name_given=dreamer.name_given,
                    name=f"{dreamer.name_family} {dreamer.name_given}",
                    enrolled_at=enrollment.enrolled_at,
                )
            )

        return StudentListResponse(items=items, total=len(all_enrollments))

    def get_student_detail(
        self, class_id: str, dreamer_id: str, mentor_id: str
    ) -> StudentDetail:
        self._require_class(class_id, mentor_id)
        enrollment_result = mentor_gateway.get_enrollment(class_id, dreamer_id)
        if not enrollment_result["success"] or not enrollment_result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="この生徒はクラスに在籍していません",
            )
        enrollment = enrollment_result["data"][0]

        dreamer_result = dreamer_gateway.get_dreamer(dreamer_id)
        if not dreamer_result["success"] or not dreamer_result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="生徒が見つかりません"
            )
        dreamer = dreamer_result["data"][0]

        history_result = job_gateway.get_history(UUID(dreamer_id))
        histories = []
        if history_result.get("success") and history_result.get("data"):
            histories = history_result["data"]

        interest_jobs: list[JobInterestSummary] = []
        liked_count = 0
        category_counts: dict[str, int] = {}

        for h in histories[:20]:
            job_id = getattr(h, "job_id", None)
            if job_id is None:
                continue
            job_resp = job_gateway.get_job(int(job_id))
            job = (
                job_resp["data"][0]
                if job_resp.get("success") and job_resp.get("data")
                else None
            )
            interest_jobs.append(
                JobInterestSummary(
                    job_id=int(job_id),
                    job_name=getattr(job, "name", str(job_id)) if job else str(job_id),
                    good=bool(getattr(h, "good", False)),
                    bad=bool(getattr(h, "bad", False)),
                    save=bool(getattr(h, "save", False)),
                )
            )
            if getattr(h, "good", False):
                liked_count += 1
            if job:
                cat = getattr(job, "category", None)
                cat_name = getattr(cat, "name", None) if cat else None
                if cat_name:
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        top_cats = sorted(category_counts, key=lambda k: -category_counts[k])[:5]

        return StudentDetail(
            dreamer_id=dreamer.dreamer_id,
            name_family=dreamer.name_family,
            name_given=dreamer.name_given,
            name=f"{dreamer.name_family} {dreamer.name_given}",
            enrolled_at=enrollment.enrolled_at,
            interest_jobs=interest_jobs,
            top_categories=top_cats,
            total_viewed=len(histories),
            liked_count=liked_count,
        )

    def add_students(
        self, class_id: str, request: EnrollmentCreateRequest, mentor_id: str
    ) -> list[EnrollmentResponse]:
        self._require_class(class_id, mentor_id)
        responses = []
        for dreamer_id in request.dreamer_ids:
            dreamer_result = dreamer_gateway.get_dreamer(str(dreamer_id))
            if not dreamer_result["success"] or not dreamer_result["data"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"生徒 {dreamer_id} が見つかりません",
                )
            existing = mentor_gateway.get_enrollment(class_id, str(dreamer_id))
            if existing["success"] and existing["data"]:
                continue
            result = mentor_gateway.create_enrollment(
                {"class_id": class_id, "dreamer_id": str(dreamer_id)}
            )
            self._ensure_success(result)
            responses.append(EnrollmentResponse.model_validate(result["data"]))
        return responses

    def remove_student(self, class_id: str, dreamer_id: str, mentor_id: str) -> dict:
        self._require_class(class_id, mentor_id)
        result = mentor_gateway.delete_enrollment(class_id, dreamer_id)
        self._ensure_success(result)
        return {"message": "生徒をクラスから削除しました"}

    # ── LessonMaterial ────────────────────────────────────────────────

    def list_materials(
        self, class_id: str, mentor_id: str, limit: int = 50, offset: int = 0
    ) -> LessonMaterialListResponse:
        self._require_class(class_id, mentor_id)
        result = mentor_gateway.list_materials(class_id)
        self._ensure_success(result)
        all_items = result["data"] or []
        paged = all_items[offset : offset + limit]
        return LessonMaterialListResponse(
            items=[LessonMaterialResponse.model_validate(m) for m in paged],
            total=len(all_items),
        )

    async def upload_material(
        self,
        class_id: str,
        mentor_id: str,
        file: UploadFile,
        title: str,
        subject: str | None = None,
        unit: str | None = None,
        description: str | None = None,
    ) -> LessonMaterialResponse:
        self._require_class(class_id, mentor_id)

        content = await file.read()
        validate_upload(file, content)

        stored = save_upload(file, content)
        text = extract_text_from_upload(stored["file_path"], stored["mime_type"])

        result = mentor_gateway.create_material(
            {
                "class_id": class_id,
                "mentor_id": mentor_id,
                "title": title,
                "subject": subject,
                "unit": unit,
                "description": description,
                "file_name": stored["file_name"],
                "file_path": stored["file_path"],
                "file_size": stored["file_size"],
                "mime_type": stored["mime_type"],
                "content_text": text or None,
                "content_hash": stored["content_hash"],
            }
        )
        self._ensure_success(result)
        return LessonMaterialResponse.model_validate(result["data"])

    def get_material(
        self, class_id: str, material_id: str, mentor_id: str
    ) -> LessonMaterialResponse:
        self._require_class(class_id, mentor_id)
        result = mentor_gateway.get_material(material_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="授業資料が見つかりません"
            )
        mat = result["data"][0]
        if str(mat.class_id) != class_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="この授業資料にはアクセスできません"
            )
        return LessonMaterialResponse.model_validate(mat)

    def update_material(
        self,
        class_id: str,
        material_id: str,
        request: LessonMaterialUpdateRequest,
        mentor_id: str,
    ) -> LessonMaterialResponse:
        self.get_material(class_id, material_id, mentor_id)
        payload = request.model_dump(exclude_none=True)
        result = mentor_gateway.update_material(material_id, payload)
        self._ensure_success(result)
        return LessonMaterialResponse.model_validate(result["data"][0])

    def delete_material(
        self, class_id: str, material_id: str, mentor_id: str
    ) -> dict:
        self.get_material(class_id, material_id, mentor_id)
        result = mentor_gateway.soft_delete_material(material_id)
        self._ensure_success(result)
        return {"message": "授業資料を削除しました", "material_id": material_id}

    # ── Analytics ─────────────────────────────────────────────────────

    def get_class_analytics(
        self, class_id: str, mentor_id: str
    ) -> ClassAnalyticsResponse:
        self._require_class(class_id, mentor_id)

        enrollment_result = mentor_gateway.list_enrollments(class_id)
        enrollments = enrollment_result["data"] if enrollment_result["success"] else []
        total_students = len(enrollments or [])

        category_counts: dict[str, int] = {}
        for enrollment in (enrollments or [])[:30]:
            history_result = job_gateway.get_history(UUID(str(enrollment.dreamer_id)))
            if not history_result.get("success"):
                continue
            for h in (history_result.get("data") or []):
                if not getattr(h, "good", False):
                    continue
                job_resp = job_gateway.get_job(int(getattr(h, "job_id", 0)))
                if not job_resp.get("success") or not job_resp.get("data"):
                    continue
                job = job_resp["data"][0]
                cat = getattr(job, "category", None)
                cat_name = getattr(cat, "name", None) if cat else None
                if cat_name:
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        top_cats = sorted(category_counts.items(), key=lambda kv: -kv[1])[:10]
        cat_distribution = [
            CategoryDistribution(category_name=k, count=v) for k, v in top_cats
        ]

        from app.gateways.dream_action_gateway import dream_action_gateway

        gen_result = dream_action_gateway.list_generated_materials_by_class(class_id)
        gen_materials = gen_result["data"] if gen_result["success"] else []
        generated_count = len(gen_materials or [])
        distributed_count = sum(
            1 for m in (gen_materials or []) if getattr(m, "status", "") == "DISTRIBUTED"
        )
        reviewing_count = sum(
            1 for m in (gen_materials or []) if getattr(m, "status", "") == "REVIEWING"
        )

        return ClassAnalyticsResponse(
            class_id=UUID(class_id),
            total_students=total_students,
            top_job_categories=cat_distribution,
            generated_materials_count=generated_count,
            distributed_materials_count=distributed_count,
            pending_review_count=reviewing_count,
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def _require_class(self, class_id: str, mentor_id: str):
        """クラスを取得しアクセス権を確認する。"""
        result = mentor_gateway.get_class(class_id)
        if not result["success"] or not result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="クラスが見つかりません",
            )
        cls = result["data"][0]
        if str(cls.mentor_id) != mentor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このクラスにはアクセスできません",
            )
        return cls

    def _ensure_success(self, result: dict):
        if result["success"]:
            return
        msg = result.get("message", ["gateway error"])
        if isinstance(msg, list):
            msg = ", ".join(msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
        )


mentor_service = MentorService()
