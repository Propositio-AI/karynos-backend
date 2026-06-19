"""
ファイルストレージユーティリティ

現在はローカルファイルシステムに保存する。
S3 等への移行時はこのモジュールだけ差し替える。
"""

import hashlib
import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from settings import settings

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/markdown",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"}


def _safe_filename(original: str) -> str:
    """元のファイル名から安全な ASCII ファイル名を生成する。"""
    stem = Path(original).stem
    suffix = Path(original).suffix.lower()
    stem_safe = re.sub(r"[^\w\-]", "_", stem)[:64]
    unique = uuid.uuid4().hex[:8]
    return f"{stem_safe}_{unique}{suffix}"


def validate_upload(file: UploadFile, content: bytes) -> None:
    """拡張子・MIME・サイズを検証する。問題があれば HTTPException を送出する。"""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていないファイル形式です: {ext}。"
            f"許可形式: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていない MIME タイプです: {file.content_type}",
        )

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ファイルサイズが上限 {settings.MAX_UPLOAD_SIZE_MB}MB を超えています",
        )


def save_upload(file: UploadFile, content: bytes, subdir: str = "materials") -> dict:
    """
    ファイルを UPLOAD_DIR/{subdir}/ に保存する。

    Returns:
        {
            "file_name": str,   # 元のファイル名
            "file_path": str,   # 保存先パス（ルートからの相対）
            "file_size": int,
            "mime_type": str,
            "content_hash": str,
        }
    """
    save_dir = Path(settings.UPLOAD_DIR) / subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_filename(file.filename or "file")
    dest = save_dir / safe_name
    dest.write_bytes(content)

    content_hash = hashlib.sha256(content).hexdigest()

    return {
        "file_name": file.filename or safe_name,
        "file_path": str(dest),
        "file_size": len(content),
        "mime_type": file.content_type or "application/octet-stream",
        "content_hash": content_hash,
    }


def delete_upload(file_path: str) -> None:
    """保存済みファイルを削除する。ファイルが存在しない場合は無視する。"""
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def extract_text_from_upload(file_path: str, mime_type: str) -> str:
    """
    アップロードされたファイルからテキストを抽出する。

    現在サポート:
    - text/plain, text/markdown: そのまま読む
    - application/pdf: pypdf があれば使用、なければ空文字
    - その他: 空文字（将来の実装で拡張）
    """
    try:
        if mime_type in ("text/plain", "text/markdown"):
            return Path(file_path).read_text(encoding="utf-8", errors="replace")

        if mime_type == "application/pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(file_path)
                pages = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages)
            except ImportError:
                pass
    except Exception:
        pass
    return ""
