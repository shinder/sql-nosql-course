"""依 ab_id 修改 public.address_book 的 name 欄位。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_update 123 王小明     # 把 ab_id=123 的 name 改成「王小明」
"""

import sys

import psycopg

from pgsql.config import get_conninfo


def main() -> None:
    # UPDATE 也是破壞性操作（會覆蓋舊資料），所以兩個參數都要明確提供，不設預設值。
    if len(sys.argv) < 3:
        sys.exit("用法：uv run python -m pgsql.run_update <ab_id> <new_name>")

    try:
        ab_id = int(sys.argv[1])
    except ValueError:
        sys.exit(f"ab_id 必須是整數（傳入：{sys.argv[1]!r}）")

    new_name = sys.argv[2]

    # %s 占位符：ab_id 跟 new_name 都用 psycopg 的安全代入機制，
    # 不要用 f-string 拼 SQL（SQL injection 的經典寫法）。
    # RETURNING ab_id, name, email：UPDATE 完直接回傳更新後的這幾欄，
    # 印出來就能確認「真的改到我想改的那一筆，而且改成了我要的值」。
    sql = """
        UPDATE public.address_book
        SET name = %s
        WHERE ab_id = %s
        RETURNING ab_id, name, email
    """

    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            # 第二個參數是 tuple，順序要跟 SQL 裡 %s 出現的順序一致：
            # SET name = %s 在前 → new_name 在前；WHERE ab_id = %s 在後 → ab_id 在後。
            cur.execute(sql, (new_name, ab_id))

            # 沒匹配的 row 時，RETURNING 不會回東西，fetchone() 會拿到 None。
            updated = cur.fetchone()

    if updated is None:
        sys.exit(f"找不到 ab_id={ab_id} 的資料，沒有更新任何東西")

    # tuple unpacking：把 RETURNING 回傳的三欄拆給三個變數
    new_ab_id, new_name_db, email = updated
    print(f"已更新 ab_id={new_ab_id}：")
    print(f"  name : {new_name_db}")
    print(f"  email: {email}（未變更，僅供辨識）")


if __name__ == "__main__":
    main()
