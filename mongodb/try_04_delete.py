"""依 ab_id 刪除 address_book 的一份文件。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_04_delete 1

對照 pgsql.try_04_delete 的差別：
    - find_one_and_delete = SQL 的 DELETE ... RETURNING *，
      原子完成「找 → 刪 → 回傳被刪的文件」
    - 也可以用 delete_one()，但只回傳 DeleteResult.deleted_count，
      不回傳被刪文件的內容。先 find_one 再 delete_one 不是原子的，
      兩個動作之間別的 client 可能改掉資料。
"""

import sys

from pymongo import MongoClient

from mongodb.config import get_db_name, get_mongo_uri


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("用法：uv run python -m mongodb.try_04_delete <ab_id>")

    try:
        ab_id = int(sys.argv[1])
    except ValueError:
        sys.exit(f"ab_id 必須是整數（傳入：{sys.argv[1]!r}）")

    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        # find_one_and_delete：找到符合 filter 的第一筆 → 刪除 → 回傳被刪文件。
        # 沒找到時回傳 None（不會拋例外）。
        # ⚠️ 不要用 delete_many({"ab_id": ab_id})。雖然 ab_id 應該唯一，
        #   但 MongoDB 沒幫你檢查（沒有 UNIQUE 約束）── delete_one / find_one_and_delete
        #   保證最多刪一筆，比較安全。要強制唯一可在 collection 上建 unique index。
        deleted = db.address_book.find_one_and_delete({"ab_id": ab_id})

    if deleted is None:
        sys.exit(f"找不到 ab_id={ab_id} 的文件，沒有刪除任何東西")

    print(f"已刪除 ab_id={ab_id}：")
    for col, val in deleted.items():
        print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
