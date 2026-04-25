"""PostgreSQL 連線基本範例。

執行方式（從專案根目錄）：
    uv run python -m pgsql.connect

連線參數從專案根目錄的 .env 讀取（請參考 .env.example 建立）：
    PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_conninfo() -> str:
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "postgres")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def main() -> None:
    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            row = cur.fetchone()
            print("PostgreSQL 版本：", row[0] if row else "(無回應)")


if __name__ == "__main__":
    main()
