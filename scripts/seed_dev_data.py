"""
開発用シードデータ投入スクリプト

使用方法:
  PYTHONPATH=/app python /app/scripts/seed_dev_data.py

Cognito が未設定の開発環境向けに、モック認証と対応するデータを作成する。
既に同じデータが存在する場合はスキップする（冪等）。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.gateways.db.prisma_client import run_prisma, prisma_client

MOCK_MENTOR_ID = "00000000-0000-0000-0000-000000000002"
MOCK_MENTOR_SUB = "mock-mentor-sub"
MOCK_DREAMER_ID = "00000000-0000-0000-0000-000000000001"
MOCK_DREAMER_SUB = "mock-dreamer-sub"


async def seed():
    client = prisma_client()
    await client.connect()

    print("=== シードデータ投入開始 ===")

    # ── Dreamer ──────────────────────────────────────────────────────
    existing_dreamer = await client.dreamer.find_first(
        where={"dreamer_id": MOCK_DREAMER_ID}
    )
    if not existing_dreamer:
        await client.dreamer.create(
            data={
                "dreamer_id": MOCK_DREAMER_ID,
                "cognito_sub": MOCK_DREAMER_SUB,
                "login_id": "mock-dreamer",
                "name_family": "田中",
                "name_given": "太郎",
            }
        )
        print(f"  ✓ Dreamer 作成: {MOCK_DREAMER_ID}")
    else:
        print(f"  - Dreamer 既存: {MOCK_DREAMER_ID}")

    # ── Mentor ───────────────────────────────────────────────────────
    existing_mentor = await client.mentor.find_first(
        where={"mentor_id": MOCK_MENTOR_ID}
    )
    if not existing_mentor:
        await client.mentor.create(
            data={
                "mentor_id": MOCK_MENTOR_ID,
                "cognito_sub": MOCK_MENTOR_SUB,
                "login_id": "mock-mentor",
                "name_family": "佐藤",
                "name_given": "花子",
                "email": "mentor@example.com",
            }
        )
        print(f"  ✓ Mentor 作成: {MOCK_MENTOR_ID}")
    else:
        print(f"  - Mentor 既存: {MOCK_MENTOR_ID}")

    # ── Class ────────────────────────────────────────────────────────
    existing_class = await client.schoolclass.find_first(
        where={"mentor_id": MOCK_MENTOR_ID}
    )
    if not existing_class:
        cls = await client.schoolclass.create(
            data={
                "mentor_id": MOCK_MENTOR_ID,
                "name": "3年A組",
                "subject": "数学",
                "description": "開発用サンプルクラス",
                "academic_year": 2025,
            }
        )
        class_id = cls.class_id
        print(f"  ✓ Class 作成: {class_id}")
    else:
        class_id = existing_class.class_id
        print(f"  - Class 既存: {class_id}")

    # ── Enrollment ───────────────────────────────────────────────────
    existing_enr = await client.enrollment.find_first(
        where={"class_id": class_id, "dreamer_id": MOCK_DREAMER_ID}
    )
    if not existing_enr:
        await client.enrollment.create(
            data={"class_id": class_id, "dreamer_id": MOCK_DREAMER_ID}
        )
        print(f"  ✓ Enrollment 作成: class={class_id} dreamer={MOCK_DREAMER_ID}")
    else:
        print(f"  - Enrollment 既存")

    # ── LessonMaterial ───────────────────────────────────────────────
    existing_mat = await client.lessonmaterial.find_first(
        where={"class_id": class_id, "is_deleted": False}
    )
    if not existing_mat:
        import os
        from pathlib import Path as P

        upload_dir = P(os.getenv("UPLOAD_DIR", "./uploads")) / "materials"
        upload_dir.mkdir(parents=True, exist_ok=True)
        sample_file = upload_dir / "sample_lesson_seed.txt"
        sample_content = (
            "# 二次方程式の解法\n\n"
            "## 単元: 因数分解と解の公式\n\n"
            "二次方程式 ax² + bx + c = 0 の解は、因数分解もしくは解の公式で求められる。\n\n"
            "### 解の公式\n"
            "x = (-b ± √(b²-4ac)) / 2a\n\n"
            "### 応用例\n"
            "- 放物線の頂点計算（物理・建築）\n"
            "- 利益最大化（経済学）\n"
            "- 信号処理（工学）\n"
        )
        sample_file.write_text(sample_content, encoding="utf-8")

        import hashlib

        mat = await client.lessonmaterial.create(
            data={
                "class_id": class_id,
                "mentor_id": MOCK_MENTOR_ID,
                "title": "二次方程式の解法（シードデータ）",
                "subject": "数学",
                "unit": "因数分解と解の公式",
                "description": "開発用サンプル授業資料",
                "file_name": "sample_lesson_seed.txt",
                "file_path": str(sample_file),
                "file_size": len(sample_content.encode()),
                "mime_type": "text/plain",
                "content_text": sample_content,
                "content_hash": hashlib.sha256(sample_content.encode()).hexdigest(),
            }
        )
        material_id = mat.material_id
        print(f"  ✓ LessonMaterial 作成: {material_id}")
    else:
        material_id = existing_mat.material_id
        print(f"  - LessonMaterial 既存: {material_id}")

    # ── 仮のいいね履歴（Dream Matching 結果のシミュレーション）────────
    # job_id=1 が存在する場合のみ作成
    first_job = await client.job.find_first()
    if first_job:
        existing_hist = await client.history.find_first(
            where={"dreamer_id": MOCK_DREAMER_ID, "job_id": first_job.job_id}
        )
        if not existing_hist:
            await client.history.create(
                data={
                    "dreamer_id": MOCK_DREAMER_ID,
                    "job_id": first_job.job_id,
                    "good": True,
                    "bad": False,
                    "save": True,
                }
            )
            print(f"  ✓ History (good) 作成: job_id={first_job.job_id}")
        else:
            print(f"  - History 既存: job_id={first_job.job_id}")
    else:
        print("  ! Job データが存在しないため History をスキップ")

    print("\n=== シードデータ投入完了 ===")
    print(f"  Mentor ID : {MOCK_MENTOR_ID}  (cognito_sub: {MOCK_MENTOR_SUB})")
    print(f"  Dreamer ID: {MOCK_DREAMER_ID}  (cognito_sub: {MOCK_DREAMER_SUB})")
    print(f"  Class ID  : {class_id}")
    print(f"  Material  : {material_id}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
