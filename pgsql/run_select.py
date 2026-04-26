"""讀取 address_book 表，依 id 由大到小取前五筆。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_select
"""

import psycopg
from psycopg.rows import dict_row

from pgsql.config import get_conninfo


def main() -> None:
    sql = "SELECT * FROM public.address_book ORDER BY ab_id DESC LIMIT 5;"

    with psycopg.connect(get_conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    if not rows:
        print("address_book 沒有資料")
        return

    print(f"共取得 {len(rows)} 筆：\n")
    for i, row in enumerate(rows, 1):
        print(f"--- 第 {i} 筆 ---")
        for col, val in row.items():
            print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
