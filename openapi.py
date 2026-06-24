import json
import subprocess
import sys
from pathlib import Path

from app.main import app

if __name__ == "__main__":
    spec_path = Path("openapi.json")
    spec_path.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[openapi] Wrote {spec_path}")

    result = subprocess.run(
        [
            "openapi-python-client",
            "generate",
            "--path",
            str(spec_path),
            "--overwrite",
        ],
        check=False,
    )
    if result.returncode != 0:
        print("[openapi] Client generation failed", file=sys.stderr)
        sys.exit(result.returncode)
    print("[openapi] Client generated: karynos-backend-client/")
