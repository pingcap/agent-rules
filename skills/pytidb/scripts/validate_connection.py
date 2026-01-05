#!/usr/bin/env python3
import os
import sys

try:
    import dotenv  # type: ignore

    dotenv.load_dotenv()
except Exception:
    pass

from pytidb import TiDBClient


def main() -> int:
    database_url = os.getenv("DATABASE_URL") or os.getenv("TIDB_DATABASE_URL")

    if database_url:
        print("=== PyTiDB connection check (database_url) ===")
        client = TiDBClient.connect(database_url=database_url)
        host_hint = database_url.split("@")[-1]
        print(f"Using DATABASE_URL (redacted): {host_hint}")
    else:
        print("=== PyTiDB connection check (params) ===")
        host = os.getenv("TIDB_HOST")
        port = int(os.getenv("TIDB_PORT", "4000"))
        username = os.getenv("TIDB_USERNAME")
        password = os.getenv("TIDB_PASSWORD", "")
        database = os.getenv("TIDB_DATABASE", "test")

        missing = [k for k in ["TIDB_HOST", "TIDB_USERNAME"] if not os.getenv(k)]
        if missing:
            print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
            return 2

        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"User: {username}")
        print(f"Database: {database}")

        client = TiDBClient.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            ensure_db=True,
        )

    try:
        val = client.query("SELECT 1 AS ok").scalar()
        if val != 1:
            print(f"Unexpected result from SELECT 1: {val}", file=sys.stderr)
            return 1
        print("✅ Connection OK")
        return 0
    except Exception as e:
        print(f"❌ Query failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
