"""讀取 address_book 表，依 id 由大到小取前五筆。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_select
"""

import psycopg

# psycopg 預設讓 fetchall() 回傳 list of tuple（每列是 tuple）。
# dict_row 是「row factory」，套用後每列改回傳 dict（key 是欄位名）。
# 好處：不用記欄位順序，可以直接 row["name"] 取值。
from psycopg.rows import dict_row

from pgsql.config import get_conninfo


def main() -> None:
    # ORDER BY ab_id DESC：依 ab_id 由大到小排序（最新的在前面）
    # LIMIT 5：最多取 5 筆
    sql = "SELECT * FROM public.address_book ORDER BY ab_id DESC LIMIT 5;"

    # row_factory=dict_row 是 connection 層級的設定，
    # 之後這條連線開的所有 cursor 都會用 dict 形式回傳結果。
    with psycopg.connect(get_conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            # fetchall() 取出所有結果列；資料量大時要小心，可能會把記憶體吃光，
            # 那種情況改用 fetchmany(N) 或直接 for row in cur 逐筆迭代比較安全。
            rows = cur.fetchall()

    # 早期 return：如果沒資料，印個訊息就結束，避免後面的迴圈跑空。
    # 比起把主邏輯包在 if rows: 裡，這種「early return」可以減少縮排層級。
    if not rows:
        print("address_book 沒有資料")
        return

    # \n 是換行字元，讓輸出多空一行比較好讀。
    print(f"共取得 {len(rows)} 筆：\n")

    # enumerate(rows, 1)：同時取出「索引」和「元素」，第二個參數 1 表示索引從 1 開始（不是 0）。
    for i, row in enumerate(rows, 1):
        print(f"--- 第 {i} 筆 ---")
        # row 是 dict，items() 同時拿出欄位名跟值。
        for col, val in row.items():
            print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
