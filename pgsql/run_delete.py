"""依 ab_id 刪除 public.address_book 的一筆資料。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_delete 123     # 刪除 ab_id=123 的那筆
"""

import sys

import psycopg
from psycopg.rows import dict_row

from pgsql.config import get_conninfo


def main() -> None:
    # 刪除是「破壞性操作」，沒給 id 直接結束比較安全（不要設預設值）。
    if len(sys.argv) < 2:
        sys.exit("用法：uv run python -m pgsql.run_delete <ab_id>")

    # 把命令列傳進來的字串轉成整數；轉不過去就讓 ValueError 噴出來給使用者看。
    # （ab_id 在資料庫是 SERIAL → INTEGER，傳字串會被 PostgreSQL 拒絕。）
    try:
        ab_id = int(sys.argv[1])
    except ValueError:
        sys.exit(f"ab_id 必須是整數（傳入：{sys.argv[1]!r}）")

    # %s 是 psycopg 的占位符，實際值由 execute() 第二個參數帶入，
    # psycopg 會自動跳脫，避免 SQL injection。
    # ⚠️ 不要寫 f"... WHERE ab_id = {ab_id}"，那是把使用者輸入直接拼進 SQL 的危險寫法。
    #
    # RETURNING *：刪除成功時把那一列的所有欄位回傳，方便確認「真的刪到我想刪的那筆」。
    # 沒有匹配的列時，RETURNING 不會回傳東西（fetchone() 會拿到 None）。
    sql = "DELETE FROM public.address_book WHERE ab_id = %s RETURNING *"

    # row_factory=dict_row 讓 fetchone() 回傳 dict 而不是 tuple，
    # 方便用欄位名取值印出來。
    with psycopg.connect(get_conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # execute() 的第二個參數一定要是「序列」（tuple 或 list），
            # 即使只有一個值也要寫成 (ab_id,)，逗號不能省 —— 沒逗號就只是普通括號，不是 tuple。
            cur.execute(sql, (ab_id,))
            deleted = cur.fetchone()

    # 沒找到符合的列：deleted 是 None，提醒使用者並用 exit code 1 結束。
    if deleted is None:
        sys.exit(f"找不到 ab_id={ab_id} 的資料，沒有刪除任何東西")

    print(f"已刪除 ab_id={ab_id}：")
    for col, val in deleted.items():
        print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
