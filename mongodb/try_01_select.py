"""讀取 address_book collection，依 ab_id 由大到小取前 5 筆。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_01_select

對照 pgsql.try_01_select 的差別：
    - 查詢條件是 dict（filter document），不是 SQL 字串
      → 不需要 placeholder（%s），dict 結構天生避開 injection 問題
    - PostgreSQL row 預設是 tuple，需要 dict_row 才能拿 dict；
      MongoDB 文件本身就是 dict，driver 直接回傳 dict
    - 沒有「資料表 schema」的概念 ── 同一 collection 的每份文件
      可以有不同欄位，find() 不會因為欄位缺失就出錯
"""

# DESCENDING / ASCENDING 是 pymongo 提供的常數，分別是 -1 / 1
from pymongo import DESCENDING, MongoClient

from mongodb.config import get_db_name, get_mongo_uri


def main() -> None:
    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        # collection.find(filter, projection) 是 SQL 的 SELECT。
        #   filter      = {} → 沒條件，相當於 SELECT * 沒 WHERE
        #   .sort()     → ORDER BY，第二參數 DESCENDING == -1
        #   .limit(N)   → LIMIT N
        # find() 回傳 cursor（lazy），真的迭代才會去 server 拿資料。
        cursor = db.address_book.find({}).sort("ab_id", DESCENDING).limit(5)

        # list(cursor) 一口氣抓完，類似 SQL 的 fetchall。
        # 資料量大時要小心，可改用 for doc in cursor: ... 逐筆處理。
        rows = list(cursor)

    if not rows:
        print("address_book 沒有資料")
        return

    print(f"共取得 {len(rows)} 筆：\n")
    for i, doc in enumerate(rows, 1):
        print(f"--- 第 {i} 筆 ---")
        # 注意：每份文件除了我們從 PG 帶過來的欄位，還會多一個 _id（ObjectId），
        # 那是 MongoDB 自動生成的主鍵；ab_id 是從 PG 沿用的整數欄位。
        for col, val in doc.items():
            print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
