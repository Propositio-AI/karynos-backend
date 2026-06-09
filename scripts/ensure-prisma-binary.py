"""
Prisma standalone query engine バイナリを確保する。

binaries.prisma.sh CDN は Python の urllib からのリクエストを拒否するため、
prisma py fetch でインストールされた Node.js 経由でダウンロードする。

取得したバイナリは named volume (/root/.cache/prisma-python) に永続化されるため
2 回目以降の起動ではダウンロードは発生しない。
"""

import json
import os
import pathlib
import platform
import struct
import subprocess
import sys
import tempfile


def _is_compatible_elf(path: pathlib.Path) -> bool:
    expected = {"aarch64": 0xB7, "x86_64": 0x3E}.get(platform.machine())
    if expected is None:
        return True
    try:
        with open(path, "rb") as f:
            if f.read(4) != b"\x7fELF":
                return True
            f.seek(18)
            (e_machine,) = struct.unpack_from("<H", f.read(2))
        return e_machine == expected
    except Exception:
        return True


def _find_compatible_binary() -> pathlib.Path | None:
    cache_root = pathlib.Path.home() / ".cache" / "prisma-python" / "binaries"
    if not cache_root.exists():
        return None
    candidates = sorted(
        [
            *cache_root.glob("*/*/prisma-query-engine-linux-arm64-openssl-*"),
            *cache_root.glob("*/*/prisma-query-engine-debian-openssl-*"),
        ],
        reverse=True,
    )
    for p in candidates:
        if p.is_file() and os.access(p, os.X_OK) and _is_compatible_elf(p):
            return p
    return None


def _find_node_binary() -> pathlib.Path | None:
    node = pathlib.Path.home() / ".cache" / "prisma-python" / "nodeenv" / "bin" / "node"
    return node if node.exists() else None


def _download_via_node(url: str, dest: pathlib.Path, node_bin: pathlib.Path) -> None:
    """Node.js の https モジュールで CDN からバイナリをダウンロードする。"""
    js = f"""
const https = require('https');
const http  = require('http');
const fs    = require('fs');
const zlib  = require('zlib');

function get(url, dest, redirects) {{
  if (redirects > 5) {{ console.error('too many redirects'); process.exit(1); }}
  const mod = url.startsWith('https') ? https : http;
  mod.get(url, (res) => {{
    if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {{
      get(res.headers.location, dest, redirects + 1);
      return;
    }}
    if (res.statusCode !== 200) {{
      console.error('HTTP ' + res.statusCode + ' ' + url);
      process.exit(1);
    }}
    const out = fs.createWriteStream(dest);
    res.pipe(zlib.createGunzip()).pipe(out);
    out.on('finish', () => {{
      fs.chmodSync(dest, 0o755);
      console.log('[prisma] saved to ' + dest);
      process.exit(0);
    }});
    out.on('error', (e) => {{ console.error(e.message); process.exit(1); }});
  }}).on('error', (e) => {{ console.error(e.message); process.exit(1); }});
}}

get({json.dumps(url)}, {json.dumps(str(dest))}, 0);
"""
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(js)
        js_path = f.name

    try:
        result = subprocess.run([str(node_bin), js_path], timeout=180)
        if result.returncode != 0:
            raise RuntimeError(f"Node.js download failed (exit {result.returncode})")
    finally:
        pathlib.Path(js_path).unlink(missing_ok=True)


def _download_binary() -> None:
    from prisma import config as prisma_config
    from prisma.binaries.platform import binary_platform, get_openssl
    from prisma.cli.prisma import ensure_cached

    engine_hash = ensure_cached().cache_dir.name
    ssl = get_openssl()
    machine = platform.machine()

    download_platform = (
        f"linux-arm64-openssl-{ssl}"
        if machine == "aarch64"
        else f"debian-openssl-{ssl}"
    )
    dest_name = f"prisma-query-engine-{binary_platform()}"

    cache_dir = prisma_config.binary_cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / dest_name

    url = f"https://binaries.prisma.sh/all_commits/{engine_hash}/{download_platform}/query-engine.gz"

    node_bin = _find_node_binary()
    if node_bin is None:
        raise RuntimeError(
            "Node.js が見つかりません。'prisma py fetch' を先に実行してください。"
        )

    print(f"[prisma] downloading {url}", flush=True)
    _download_via_node(url, dest, node_bin)


def main() -> None:
    if os.environ.get("PRISMA_QUERY_ENGINE_BINARY"):
        return

    binary = _find_compatible_binary()
    if binary:
        print(f"[prisma] found: {binary}", flush=True)
        return

    print(f"[prisma] no compatible binary for {platform.machine()}", flush=True)

    # Node.js をインストール (prisma py fetch が nodeenv をセットアップする)
    node_bin = _find_node_binary()
    if node_bin is None:
        print("[prisma] installing Node.js via prisma py fetch...", flush=True)
        subprocess.run(["prisma", "py", "fetch"], check=True)

    _download_binary()

    if not _find_compatible_binary():
        print(
            "[prisma] ERROR: download succeeded but binary is not usable",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    print("[prisma] ready", flush=True)


if __name__ == "__main__":
    main()
