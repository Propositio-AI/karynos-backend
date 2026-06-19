"""プロンプトテンプレートのロードと変数差し込み。"""

from pathlib import Path

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(template_path: str, **variables: str) -> str:
    """
    プロンプトテンプレートを読み込み、変数を差し込んで返す。

    Args:
        template_path: prompts/ 以下のパス（例: "dream_action/generate_material.txt"）
        **variables: テンプレート内の {variable_name} に差し込む値
    """
    full_path = _PROMPT_DIR / template_path
    if not full_path.exists():
        raise FileNotFoundError(f"プロンプトテンプレートが見つかりません: {full_path}")

    template = full_path.read_text(encoding="utf-8")
    return template.format(**variables)
