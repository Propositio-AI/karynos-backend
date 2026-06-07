import json
from pathlib import Path

from app.main import app


if __name__ == "__main__":
    output_path = Path("openapi.json")
    output_path.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8")
