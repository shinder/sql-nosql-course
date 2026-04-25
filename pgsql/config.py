"""連線設定來源。

從專案根目錄的 .env 讀取 PostgreSQL 連線參數，組成 conninfo 字串。
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_conninfo() -> str:
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "postgres")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"
