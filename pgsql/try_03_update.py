"""依 ab_id 修改 public.address_book 的 name 欄位，並示範 updated_at trigger。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_03_update 123 王小明     # 把 ab_id=123 的 name 改成「王小明」
"""

import sys

import psycopg

from pgsql.config import get_conninfo


def main() -> None:
    # UPDATE 也是破壞性操作（會覆蓋舊資料），所以兩個參數都要明確提供，不設預設值。
    if len(sys.argv) < 3:
        sys.exit("用法：uv run python -m pgsql.try_03_update <ab_id> <new_name>")

    try:
        ab_id = int(sys.argv[1])
    except ValueError:
        sys.exit(f"ab_id 必須是整數（傳入：{sys.argv[1]!r}）")

    new_name = sys.argv[2]

    # 使用一條連線完成「先查現況 → 再更新」兩個步驟。
    # 兩個 SQL 在同一個 transaction 裡，UPDATE 走的就是我們剛剛 SELECT 出來的那一筆。
    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            # 先把更新「前」的 name / updated_at 撈出來，等下要跟更新後對比。
            cur.execute(
                "SELECT name, updated_at FROM public.address_book WHERE ab_id = %s",
                (ab_id,),
            )
            before = cur.fetchone()
            if before is None:
                sys.exit(f"找不到 ab_id={ab_id} 的資料，沒有更新任何東西")
            old_name, old_updated_at = before

            # %s 占位符：ab_id 跟 new_name 都用 psycopg 的安全代入機制，
            # 不要用 f-string 拼 SQL（SQL injection 的經典寫法）。
            # RETURNING：UPDATE 完直接回傳更新後的欄位，印出來就能確認改對了。
            # ⭐ 這裡列 updated_at 是為了示範 trigger ── 我們的 SQL 沒去碰它，
            # 但 trigger 會在 UPDATE 發生時自動把它設成 CURRENT_TIMESTAMP。
            cur.execute(
                """
                UPDATE public.address_book
                SET name = %s
                WHERE ab_id = %s
                RETURNING name, updated_at
                """,
                (new_name, ab_id),
            )
            # 第二個參數是 tuple，順序要跟 SQL 裡 %s 出現的順序一致：
            # SET name = %s 在前 → new_name 在前；WHERE ab_id = %s 在後 → ab_id 在後。
            new_name_db, new_updated_at = cur.fetchone()

    print(f"已更新 ab_id={ab_id}：\n")
    print(f"           {'更新前':<28}  →  更新後")
    print(f"  name      {old_name!s:<28}  →  {new_name_db}")
    print(f"  updated_at {old_updated_at!s:<27}  →  {new_updated_at}")
    print("\n注意：SQL 沒有改 updated_at，是 trigger `address_book_set_updated_at`")
    print("自動把它設成 CURRENT_TIMESTAMP（見 data/shin02-pgsql.sql）。")


if __name__ == "__main__":
    main()
