from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "app" / "app" / "gen" / "prisma" / "schema.prisma"
    app_gen_dir = project_root / "app" / "app" / "gen"

    app_gen_dir.mkdir(parents=True, exist_ok=True)

    (app_gen_dir / "__init__.py").write_text("", encoding="utf-8")

    subprocess.run(
        ["prisma", "generate", "--schema", str(schema_path)],
        cwd=project_root,
        check=True,
    )

    sys.path.insert(0, str(project_root))
    importlib.invalidate_caches()


if __name__ == "__main__":
    main()
