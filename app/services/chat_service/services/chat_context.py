from app.services.chat_service.services.external.job_api import get_job_data
from pathlib import Path


def get_messages_for_openai(conversation_id: str, crud):
    response = crud.read([["conversation_id", "==", conversation_id]])
    if not response["success"]:
        raise Exception(f"会話履歴の取得に失敗しました: {', '.join(response['message'])}")

    messages_openai = []
    for message in response["data"]:
        role = getattr(message, "role", "user")
        role_value = role.value if hasattr(role, "value") else str(role)
        messages_openai.append(
            {
                "role": role_value,
                "content": getattr(message, "text_content", ""),
            }
        )
    return messages_openai


def create_system_prompt(job_data: dict, prompt_path: str | None = None) -> str:
    if prompt_path is None:
        prompt_path = str(Path(__file__).resolve().parents[1] / "prompts" / "character_prompt.txt")
    context = {
        "ai_name": "アシスタント",
        "ai_gender": "unisex",
        "job_name": job_data.get("name", ""),
        "age": job_data.get("age", 0),
        "tenure_years": job_data.get("tenure_years", 0),
        "description": job_data.get("description", ""),
        "salary": job_data.get("salary", 0),
        "end_time": job_data.get("end_time", ""),
        "overtime_hours": job_data.get("overtime_hours", 0),
        "holiday": job_data.get("holiday", 0),
        "gender_ratio": job_data.get("gender_ratio", 0),
        "gender_ratio_female": 100 - float(job_data.get("gender_ratio", 0) or 0),
        "romance_rate": job_data.get("romance_rate", 0),
        "uniform_status": "あり" if job_data.get("uniform") else "なし（私服）",
        "skills_str": ", ".join([s.get("name", "") for s in job_data.get("skills", []) if s.get("is_required", True)]),
        "certifications_str": ", ".join([c.get("name", "") for c in job_data.get("certifications", [])]),
        "interests_str": ", ".join([i.get("name", "") for i in job_data.get("interests", [])]),
        "talents_str": ", ".join([t.get("name", "") for t in job_data.get("talents", [])]),
        "companies_str": ", ".join([c.get("name", "") for c in job_data.get("companies", [])]),
    }
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    return prompt_template.format(**context)


async def build_openai_messages(
    conversation_id: str,
    job_id: str,
    messages_crud,
    system_prompt_path: str | None = None,
):
    messages = get_messages_for_openai(conversation_id, messages_crud)
    job_data = await get_job_data(job_id)
    system_prompt = create_system_prompt(job_data, prompt_path=system_prompt_path)
    messages.insert(0, {"role": "system", "content": system_prompt})
    return messages
