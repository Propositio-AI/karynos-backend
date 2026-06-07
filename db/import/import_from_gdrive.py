import csv
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Any

import psycopg2
import requests
from psycopg2 import sql
from psycopg2 import OperationalError


def env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return value


def parse_bool(value: str, default: bool = False) -> bool:
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def convert_google_drive_url(raw_url: str) -> str:
    file_match = re.search(r"/file/d/([^/]+)", raw_url)
    if file_match:
        return f"https://drive.google.com/uc?export=download&id={file_match.group(1)}"

    open_match = re.search(r"[?&]id=([^&]+)", raw_url)
    if open_match:
        return f"https://drive.google.com/uc?export=download&id={open_match.group(1)}"

    return raw_url


def is_placeholder_url(url: str) -> bool:
    return "REPLACE_WITH_FILE_ID" in url


def resolve_local_csv_path(raw_url: str) -> str | None:
    text = (raw_url or "").strip()
    if not text:
        return None

    if text.startswith("file://"):
        parsed = urlparse(text)
        local_path = unquote(parsed.path or "")
        if os.name == "nt" and local_path.startswith("/") and len(local_path) >= 3 and local_path[2] == ":":
            local_path = local_path[1:]
        if local_path and os.path.exists(local_path):
            return local_path
        return None

    as_path = Path(text)
    if as_path.exists():
        return str(as_path.resolve())

    return None


def download_csv(url: str) -> tuple[str, bool]:
    local_csv = resolve_local_csv_path(url)
    if local_csv:
        return local_csv, False

    resolved_url = convert_google_drive_url(url)
    response = requests.get(resolved_url, timeout=60)
    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp.write(response.content)
    tmp.flush()
    tmp.close()
    return tmp.name, True


def get_db_connection() -> psycopg2.extensions.connection:
    host = env("POSTGRES_SERVER", "karynos-db")
    port = env("POSTGRES_PORT", "5432")
    dbname = env("POSTGRES_DB", "karynos")
    user = env("POSTGRES_USER", "karynos")
    password = env("POSTGRES_PASSWORD", "karynos")
    retries = int(env("CSV_IMPORT_DB_CONNECT_RETRIES", "30"))
    interval_seconds = float(env("CSV_IMPORT_DB_CONNECT_INTERVAL_SECONDS", "2"))

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password,
            )
        except OperationalError as exc:
            last_error = exc
            print(
                f"[csv-import] db connection attempt {attempt}/{retries} failed: {exc}. retrying...",
                flush=True,
            )
            if attempt < retries:
                time.sleep(interval_seconds)

    raise OperationalError(
        f"failed to connect to db after {retries} attempts: {last_error}"
    )


def table_exists(cur: psycopg2.extensions.cursor, table_name: str) -> bool:
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (table_name,),
    )
    return bool(cur.fetchone()[0])


def table_row_count(cur: psycopg2.extensions.cursor, table_name: str) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(table_name))
    cur.execute(query)
    return int(cur.fetchone()[0])


def copy_csv(
    cur: psycopg2.extensions.cursor,
    table_name: str,
    csv_path: str,
    truncate: bool,
) -> tuple[int, int, int]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

    # Load CSV into a temporary unconstrained table first.
    # This allows a safe upsert into the real table and skips duplicate keys.
    staging_table_name = f"tmp_import_{table_name}"
    cur.execute(sql.SQL("DROP TABLE IF EXISTS {};").format(sql.Identifier(staging_table_name)))
    cur.execute(
        sql.SQL("CREATE TEMP TABLE {} AS SELECT {} FROM {} WITH NO DATA;").format(
            sql.Identifier(staging_table_name),
            sql.SQL(", ").join(sql.Identifier(header.strip()) for header in headers),
            sql.Identifier(table_name),
        )
    )

    copy_query = sql.SQL("COPY {} ({}) FROM STDIN WITH CSV HEADER").format(
        sql.Identifier(staging_table_name),
        sql.SQL(", ").join(sql.Identifier(header.strip()) for header in headers),
    )

    with open(csv_path, "r", encoding="utf-8") as f:
        cur.copy_expert(copy_query.as_string(cur.connection), f)

    cur.execute(sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(staging_table_name)))
    staged_rows = int(cur.fetchone()[0])

    if truncate:
        cur.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(sql.Identifier(table_name)))

    insert_query = sql.SQL(
        "INSERT INTO {} ({}) SELECT {} FROM {} ON CONFLICT DO NOTHING;"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(header.strip()) for header in headers),
        sql.SQL(", ").join(sql.Identifier(header.strip()) for header in headers),
        sql.Identifier(staging_table_name),
    )
    cur.execute(insert_query)
    inserted_rows = cur.rowcount

    return table_row_count(cur, table_name), staged_rows, inserted_rows


def load_config(config_path: str) -> list[dict[str, Any]]:
    if not os.path.exists(config_path):
        print(f"[csv-import] config file not found: {config_path}. skip import.")
        return []

    import json

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tables = data.get("tables", [])
    if not isinstance(tables, list):
        raise ValueError("config.tables must be a list")
    return tables


def main() -> None:
    config_path = env("CSV_IMPORT_CONFIG_JSON", "/opt/db_import/table_sources.json")
    skip_if_has_data = parse_bool(env("CSV_IMPORT_SKIP_IF_TABLE_HAS_DATA", "true"), default=True)
    table_configs = load_config(config_path)

    if not table_configs:
        print("[csv-import] no table config found. done.")
        return

    conn = get_db_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            for item in table_configs:
                table_name = item.get("table")
                csv_url = item.get("url")
                truncate = bool(item.get("truncate", False))

                if not table_name or not csv_url:
                    print(f"[csv-import] invalid item: {item}")
                    continue

                if is_placeholder_url(csv_url):
                    print(f"[csv-import] placeholder url for table '{table_name}'. skip.")
                    continue

                if not table_exists(cur, table_name):
                    print(f"[csv-import] table not found: {table_name}. skip.")
                    continue

                current_count = table_row_count(cur, table_name)
                if skip_if_has_data and current_count > 0 and not truncate:
                    print(f"[csv-import] table '{table_name}' already has {current_count} rows. skip.")
                    continue

                tmp_csv_path, is_temp_file = download_csv(csv_url)
                try:
                    new_count, staged_rows, inserted_rows = copy_csv(cur, table_name, tmp_csv_path, truncate)
                    conn.commit()
                    skipped_rows = max(staged_rows - inserted_rows, 0)
                    print(
                        f"[csv-import] imported table '{table_name}' rows={new_count} "
                        f"(staged={staged_rows}, inserted={inserted_rows}, skipped_duplicates={skipped_rows})"
                    )
                finally:
                    if is_temp_file and os.path.exists(tmp_csv_path):
                        os.remove(tmp_csv_path)

    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        conn.close()


if __name__ == "__main__":
    main()
