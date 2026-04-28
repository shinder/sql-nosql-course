"""依 ab_id 修改 address_book 的 name，並用 $currentDate 取代 PG 的 trigger。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_03_update 1 王小明

對照 pgsql.try_03_update 的差別：
    - PG 在 address_book 上有 BEFORE UPDATE trigger 自動更新 updated_at；
      MongoDB 沒有 DB 層級的 trigger（Atlas 有 trigger 服務但不是同一回事），
      改用 update operator $currentDate 在每次 UPDATE 主動寫入 server 當前時間。
    - 用 update operators ($set / $inc / $push / $currentDate ...) 只改指定欄位，
      不用整份文件重寫。對應 SQL 的 UPDATE ... SET col = ...。
    - find_one_and_update + ReturnDocument.AFTER 一次完成「更新 + 拿到結果」，
      相當於 SQL 的 UPDATE ... RETURNING。

設計上的差異：
    PG 的 trigger 在資料庫層級執行，繞過 driver 直接 SQL UPDATE 也會觸發；
    MongoDB 的 $currentDate 是 driver 端推上去的，繞過 driver 改資料就不會更新。
    取捨：MongoDB 邏輯都在程式裡（透明、可測），PG trigger 強制保證（沒人能繞）。
"""

import sys

from pymongo import MongoClient, ReturnDocument

from mongodb.config import get_db_name, get_mongo_uri


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("用法：uv run python -m mongodb.try_03_update <ab_id> <new_name>")

    try:
        ab_id = int(sys.argv[1])
    except ValueError:
        sys.exit(f"ab_id 必須是整數（傳入：{sys.argv[1]!r}）")

    new_name = sys.argv[2]

    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        # 先抓更新前的狀態（updated_at 一起拿，等下要比對）
        before = db.address_book.find_one({"ab_id": ab_id})
        if before is None:
            sys.exit(f"找不到 ab_id={ab_id} 的文件，沒有更新任何東西")

        # find_one_and_update：原子操作，一次做「找+更新+回傳」。
        #   filter           : 哪一筆要被改
        #   update           : 改什麼，用 update operators 表達
        #     $set          設定欄位（這裡改 name）
        #     $currentDate  把欄位設成 server 當前時間 ── 這就是取代 PG trigger 的關鍵
        #   return_document  : ReturnDocument.AFTER → 回傳更新後的文件
        #                       （預設是 BEFORE，會回傳更新前的 ── 容易踩坑）
        #
        # ⚠️ 注意：$currentDate 是 **update operator**，只能用在 update 語境
        #   （update_one / update_many / find_one_and_update / bulk_write 的 update ops）。
        #   insert_one / insert_many 收的是字面文件，把 $currentDate 寫進去會變成
        #   一個叫 "$currentDate" 的詭異欄位，不會被 server 解讀為運算子。
        #   想在 insert 時用 server-side 時間，要嘛改用 update_one + upsert=True
        #   配 $setOnInsert，要嘛 client 端用 datetime.now(timezone.utc)
        #   （見 try_02_insert.py 的作法）。
        after = db.address_book.find_one_and_update(
            {"ab_id": ab_id},
            {
                "$set": {"name": new_name},
                "$currentDate": {"updated_at": True},
            },
            return_document=ReturnDocument.AFTER,
        )

    print(f"已更新 ab_id={ab_id}：\n")
    print(f"  {'欄位':<12}{'更新前':<28}  →  更新後")
    print(f"  {'name':<12}{before.get('name')!s:<28}  →  {after['name']}")
    print(f"  {'updated_at':<12}{before.get('updated_at')!s:<28}  →  {after['updated_at']}")
    print("\nMongoDB 沒有 DB 層級的 trigger，updated_at 是用 update operator")
    print("`$currentDate` 在每次 UPDATE 時主動寫入。")


if __name__ == "__main__":
    main()
