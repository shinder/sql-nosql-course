"""PostgreSQL 連線基本範例。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_connect
"""

import psycopg

from pgsql.config import get_conninfo


def main() -> None:
    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            row = cur.fetchone()
            print("PostgreSQL 版本：", row[0] if row else "(無回應)")


if __name__ == "__main__":
    main()
