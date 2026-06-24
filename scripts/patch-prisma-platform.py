"""
prisma-client-py 0.15.0 の ARM64 プラットフォーム検出バグを修正する。

ARM64 (aarch64) Linux では binary_platform() が誤って 'debian-openssl-*' を返す。
このスクリプトはインストール済み prisma パッケージの platform.py を直接パッチし、
'linux-arm64-openssl-*' を返すよう修正する。
`prisma py fetch` の前に実行すること。
"""

import importlib.util
import pathlib
import platform
import sys

machine = platform.machine()
if machine != "aarch64":
    print(f"[patch] ARM64 以外 ({machine}), スキップ", file=sys.stderr)
    sys.exit(0)

spec = importlib.util.find_spec("prisma")
assert spec and spec.origin, "prisma パッケージが見つかりません"
platform_py = pathlib.Path(spec.origin).parent / "binaries" / "platform.py"

original = platform_py.read_text()
if "aarch64" in original:
    print("[patch] 適用済み, スキップ", file=sys.stderr)
    sys.exit(0)

patch = """
# ---- ARM64 fix (patched by scripts/patch_prisma_platform.py) ----
_orig_binary_platform = binary_platform

def binary_platform() -> str:  # type: ignore[no-redef]
    import platform as _p
    if _p.machine() == "aarch64":
        return "linux-arm64-openssl-" + get_openssl()
    return _orig_binary_platform()
"""

platform_py.write_text(original + patch)
print(f"[patch] {platform_py} にパッチを適用しました", file=sys.stderr)
