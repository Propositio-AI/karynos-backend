import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5


def _clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _to_int(value: str | None, default: int = 0) -> int:
    text = _clean_text(value)
    if not text:
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def _to_int_nullable(value: str | None) -> int | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        # DBカラムがINTEGERのため、小数値は四捨五入して整数化する。
        return int(round(float(text)))
    except ValueError:
        return None


def _to_float_nullable(value: str | None) -> float | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _split_csv_cell(value: str | None) -> list[str]:
    text = _clean_text(value)
    if not text:
        return []
    return [token.strip() for token in text.split(",") if token.strip()]


def _merge_tokens(*values: str | None, sep: str = ", ") -> str:
    merged: list[str] = []
    for value in values:
        for token in _split_csv_cell(value):
            if token not in merged:
                merged.append(token)
    return sep.join(merged)


def _make_growth_opportunities(industry: str | None, job_type: str | None) -> str:
    parts = []
    industry_text = _clean_text(industry)
    if industry_text:
        parts.append(f"産業分野: {industry_text}")

    job_type_text = _clean_text(job_type)
    if job_type_text:
        parts.append(f"職種: {job_type_text}")

    return " / ".join(parts)


def _parse_bool_token(token: str) -> bool:
    normalized = token.strip().lower()
    return normalized in {"true", "1", "yes", "y", "t"}


def _parse_bool_list(value: str | None) -> list[bool]:
    tokens = _split_csv_cell(value)
    return [_parse_bool_token(token) for token in tokens]


def _normalize_time(value: str | None) -> str | None:
    text = _clean_text(value)
    if not text:
        return None

    parts = text.split(":")
    if len(parts) == 2:
        hh, mm = parts
        if hh.isdigit() and mm.isdigit():
            return f"{int(hh):02d}:{int(mm):02d}:00"
    if len(parts) == 3:
        hh, mm, ss = parts
        if hh.isdigit() and mm.isdigit() and ss.isdigit():
            return f"{int(hh):02d}:{int(mm):02d}:{int(ss):02d}"

    return None


def _derive_level(salary: int | None) -> int | None:
    if salary is None or salary <= 0:
        return None
    if salary <= 400:
        return 1
    if salary <= 550:
        return 2
    if salary <= 700:
        return 3
    if salary <= 900:
        return 4
    return 5


def _pad_bool_list(flags: list[bool], length: int) -> list[bool]:
    if length <= 0:
        return []
    if not flags:
        return [False] * length
    if len(flags) == 1 and length > 1:
        return [flags[0]] * length
    if len(flags) >= length:
        return flags[:length]
    return flags + [False] * (length - len(flags))


def _upsert_master_id(master: dict[str, int], value: str) -> int:
    if value not in master:
        master[value] = len(master) + 1
    return master[value]


def _feedback_uuid(job_id: int) -> str:
    return str(uuid5(NAMESPACE_DNS, f"karynos-job-feedback-{job_id}"))


def convert_row(row: dict[str, str]) -> dict[str, object]:
    return {
        "job_id": _to_int(row.get("ID")),
        "name": _clean_text(row.get("職業名")),
        "description": _clean_text(row.get("職業概要")),
        "salary": _to_int(row.get("年収")),
        "age": _to_int(row.get("平均年齢")),
        "personality_traits": _merge_tokens(row.get("才能名"), row.get("スキル名")),
        "appeal_points": _merge_tokens(row.get("興味・関心"), row.get("会社名")),
        "growth_opportunities": _make_growth_opportunities(row.get("産業分野"), row.get("職種")),
    }


def build_db_ready_dataset(input_csv: Path) -> dict[str, object]:
    industry_ids: dict[str, int] = {}
    category_ids: dict[str, int] = {}
    skill_ids: dict[str, int] = {}
    certification_ids: dict[str, int] = {}
    company_ids: dict[str, int] = {}
    talent_ids: dict[str, int] = {}
    interest_ids: dict[str, int] = {}

    jobs: list[dict[str, object]] = []
    job_feedbacks: list[dict[str, object]] = []
    feedback_skill: list[dict[str, object]] = []
    feedback_certification: list[dict[str, object]] = []
    feedback_company: list[dict[str, object]] = []
    feedback_talent: list[dict[str, object]] = []
    feedback_interest: list[dict[str, object]] = []

    seen_job_ids: set[int] = set()

    with input_csv.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            job_id = _to_int(row.get("ID"))
            name = _clean_text(row.get("職業名"))
            if not job_id or not name:
                continue

            if job_id in seen_job_ids:
                continue

            seen_job_ids.add(job_id)

            industry_name = _clean_text(row.get("産業分野"))
            category_name = _clean_text(row.get("職種"))

            if not industry_name:
                industry_name = "未分類"
            if not category_name:
                category_name = "未分類"

            industry_id = _upsert_master_id(industry_ids, industry_name)
            category_id = _upsert_master_id(category_ids, category_name)

            description = _clean_text(row.get("職業概要"))
            jobs.append(
                {
                    "job_id": job_id,
                    "industry_id": industry_id,
                    "category_id": category_id,
                    "name": name,
                    "description": description or None,
                }
            )

            salary = _to_int_nullable(row.get("年収"))
            level = _derive_level(salary)
            age = _to_int_nullable(row.get("平均年齢"))
            holiday = _to_int_nullable(row.get("平均休日日数"))
            overtime_hours = _to_int_nullable(row.get("残業時間"))
            marriage_age = _to_int_nullable(row.get("結婚年齢"))
            tenure_years = _to_int_nullable(row.get("平均滞在年"))
            gender_ratio = _to_float_nullable(row.get("男性率"))
            romance_rate = _to_float_nullable(row.get("結婚率"))
            end_time = _normalize_time(row.get("平均代謝時刻"))

            feedback_id = _feedback_uuid(job_id)
            job_feedbacks.append(
                {
                    "feedback_id": feedback_id,
                    "job_id": job_id,
                    "salary": salary,
                    "level": level,
                    "end_time": end_time,
                    "holiday": holiday,
                    "overtime_hours": overtime_hours,
                    "age": age,
                    "tenure_years": tenure_years,
                    "marriage_age": marriage_age,
                    "gender_ratio": gender_ratio,
                    "romance_rate": romance_rate,
                    "social_signification": _clean_text(row.get("起源")) or None,
                    "personality_traits": _merge_tokens(row.get("才能名"), row.get("スキル名")) or None,
                    "growth_opportunities": _make_growth_opportunities(industry_name, category_name) or None,
                    "wrong_image": None,
                    "uniform": None,
                    "work_life_balance": None,
                    "future_outlook": None,
                    "rarity": None,
                    "scandal_history": None,
                    "focus_on_education": any(_parse_bool_list(row.get("その資格が必須かどうか"))),
                    "focus_on_achievements": any(_parse_bool_list(row.get("そのスキルが必須かどうか"))),
                    "appeal_points": _merge_tokens(row.get("興味・関心"), row.get("会社名")) or None,
                    "daily_routine": None,
                    "comments": None,
                }
            )

            skill_names = _split_csv_cell(row.get("スキル名"))
            skill_required = _pad_bool_list(_parse_bool_list(row.get("そのスキルが必須かどうか")), len(skill_names))
            for skill_name, is_required in zip(skill_names, skill_required):
                skill_id = _upsert_master_id(skill_ids, skill_name)
                feedback_skill.append(
                    {
                        "feedback_id": feedback_id,
                        "skill_id": skill_id,
                        "is_required": bool(is_required),
                    }
                )

            certification_names = _split_csv_cell(row.get("資格名"))
            cert_required = _pad_bool_list(
                _parse_bool_list(row.get("その資格が必須かどうか")),
                len(certification_names),
            )
            for certification_name, is_required in zip(certification_names, cert_required):
                certification_id = _upsert_master_id(certification_ids, certification_name)
                feedback_certification.append(
                    {
                        "feedback_id": feedback_id,
                        "certification_id": certification_id,
                        "is_required": bool(is_required),
                    }
                )

            company_names = _split_csv_cell(row.get("会社名"))
            for company_name in company_names:
                company_id = _upsert_master_id(company_ids, company_name)
                feedback_company.append(
                    {
                        "feedback_id": feedback_id,
                        "company_id": company_id,
                    }
                )

            talent_names = _split_csv_cell(row.get("才能名"))
            talent_required = _pad_bool_list(_parse_bool_list(row.get("その才能が必須かどうか")), len(talent_names))
            for talent_name, is_required in zip(talent_names, talent_required):
                talent_id = _upsert_master_id(talent_ids, talent_name)
                feedback_talent.append(
                    {
                        "feedback_id": feedback_id,
                        "talent_id": talent_id,
                        "is_required": bool(is_required),
                    }
                )

            interest_names = _split_csv_cell(row.get("興味・関心"))
            interest_required = _pad_bool_list(
                _parse_bool_list(row.get("その興味・関心が必須かどうか")),
                len(interest_names),
            )
            for interest_name, is_required in zip(interest_names, interest_required):
                interest_id = _upsert_master_id(interest_ids, interest_name)
                feedback_interest.append(
                    {
                        "feedback_id": feedback_id,
                        "interest_id": interest_id,
                        "is_required": bool(is_required),
                    }
                )

    def to_master_rows(master: dict[str, int], id_col: str) -> list[dict[str, object]]:
        return [{id_col: value_id, "name": name} for name, value_id in master.items()]

    payload = {
        "generated_at": datetime.now().isoformat(),
        "source_file": str(input_csv),
        "counts": {
            "industries": len(industry_ids),
            "job_categories": len(category_ids),
            "skills": len(skill_ids),
            "certifications": len(certification_ids),
            "companies": len(company_ids),
            "talents": len(talent_ids),
            "interests": len(interest_ids),
            "jobs": len(jobs),
            "job_feedbacks": len(job_feedbacks),
            "feedback_skill": len(feedback_skill),
            "feedback_certification": len(feedback_certification),
            "feedback_company": len(feedback_company),
            "feedback_talent": len(feedback_talent),
            "feedback_interest": len(feedback_interest),
        },
        "tables": {
            "industries": to_master_rows(industry_ids, "industry_id"),
            "job_categories": to_master_rows(category_ids, "category_id"),
            "skills": to_master_rows(skill_ids, "skill_id"),
            "certifications": to_master_rows(certification_ids, "certification_id"),
            "companies": to_master_rows(company_ids, "company_id"),
            "talents": to_master_rows(talent_ids, "talent_id"),
            "interests": to_master_rows(interest_ids, "interest_id"),
            "jobs": jobs,
            "job_feedbacks": job_feedbacks,
            "feedback_skill": feedback_skill,
            "feedback_certification": feedback_certification,
            "feedback_company": feedback_company,
            "feedback_talent": feedback_talent,
            "feedback_interest": feedback_interest,
        },
    }

    return payload


def _write_json(path: Path, payload: dict[str, object] | list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as target:
        json.dump(payload, target, ensure_ascii=False, indent=2)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    columns = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            formatted: dict[str, object] = {}
            for col in columns:
                value = row.get(col)
                if value is None:
                    formatted[col] = ""
                elif isinstance(value, bool):
                    formatted[col] = "true" if value else "false"
                else:
                    formatted[col] = value
            writer.writerow(formatted)


def _sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("'", "''")
    return f"'{text}'"


def _build_insert_sql(tables: dict[str, list[dict[str, object]]]) -> str:
    order = [
        "industries",
        "job_categories",
        "skills",
        "certifications",
        "companies",
        "talents",
        "interests",
        "jobs",
        "job_feedbacks",
        "feedback_skill",
        "feedback_certification",
        "feedback_company",
        "feedback_talent",
        "feedback_interest",
    ]

    lines: list[str] = [
        "BEGIN;",
        "",
    ]

    for table_name in order:
        rows = tables.get(table_name, [])
        if not rows:
            continue

        columns = list(rows[0].keys())
        col_sql = ", ".join(columns)

        lines.append(f"-- {table_name}")
        for row in rows:
            values_sql = ", ".join(_sql_literal(row.get(col)) for col in columns)
            lines.append(
                f"INSERT INTO {table_name} ({col_sql}) VALUES ({values_sql}) ON CONFLICT DO NOTHING;"
            )
        lines.append("")

    lines.extend(
        [
            "SELECT setval('industries_industry_id_seq', COALESCE((SELECT MAX(industry_id) FROM industries), 1), true);",
            "SELECT setval('job_categories_category_id_seq', COALESCE((SELECT MAX(category_id) FROM job_categories), 1), true);",
            "SELECT setval('skills_skill_id_seq', COALESCE((SELECT MAX(skill_id) FROM skills), 1), true);",
            "SELECT setval('certifications_certification_id_seq', COALESCE((SELECT MAX(certification_id) FROM certifications), 1), true);",
            "SELECT setval('companies_company_id_seq', COALESCE((SELECT MAX(company_id) FROM companies), 1), true);",
            "SELECT setval('talents_talent_id_seq', COALESCE((SELECT MAX(talent_id) FROM talents), 1), true);",
            "SELECT setval('interests_interest_id_seq', COALESCE((SELECT MAX(interest_id) FROM interests), 1), true);",
            "SELECT setval('jobs_job_id_seq', COALESCE((SELECT MAX(job_id) FROM jobs), 1), true);",
            "",
            "COMMIT;",
            "",
        ]
    )

    return "\n".join(lines)


def _build_local_table_source_config(output_dir: Path, table_names: list[str]) -> dict[str, object]:
    tables: list[dict[str, object]] = []
    for table_name in table_names:
        csv_path = (output_dir / f"{table_name}.csv").resolve()
        csv_uri = csv_path.as_uri()
        tables.append(
            {
                "table": table_name,
                "url": csv_uri,
                "truncate": False,
            }
        )
    return {"tables": tables}


def generate_test_data(input_csv: Path, output_dir: Path) -> dict[str, object]:
    payload = build_db_ready_dataset(input_csv)
    tables = payload["tables"]
    table_names = list(tables.keys())

    output_dir.mkdir(parents=True, exist_ok=True)
    for table_name, rows in tables.items():
        _write_json(output_dir / f"{table_name}.json", rows)
        _write_csv(output_dir / f"{table_name}.csv", rows)

    _write_json(output_dir / "seed_bundle.json", payload)

    sql_text = _build_insert_sql(tables)
    (output_dir / "seed_insert.sql").write_text(sql_text, encoding="utf-8")

    local_config = _build_local_table_source_config(output_dir=output_dir, table_names=table_names)
    _write_json(output_dir / "table_sources.local.json", local_config)

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="職業CSVからDB投入向けtest_data(CSV/JSON/SQL)を生成します")
    parser.add_argument("--input", required=True, help="入力CSVファイルパス")
    parser.add_argument(
        "--output-dir",
        default="db/import/generated",
        help="出力ディレクトリパス（テーブル別CSV/JSONを生成）",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.exists():
        print(json.dumps({"ok": False, "message": f"input not found: {input_path}"}, ensure_ascii=False))
        return 1

    payload = generate_test_data(input_csv=input_path, output_dir=output_dir)

    print(
        json.dumps(
            {
                "ok": True,
                "output_dir": str(output_dir),
                "jobs_count": payload["counts"]["jobs"],
                "job_feedbacks_count": payload["counts"]["job_feedbacks"],
                "generated_at": payload["generated_at"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
