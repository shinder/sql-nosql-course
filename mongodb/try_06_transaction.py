"""示範 MongoDB multi-document transaction ── 對照 pgsql.try_06_transaction。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_06_transaction

⚠️ 重要前置：MongoDB 的 transaction **需要 replica set**（standalone mongod 不支援）。
   如果連到的是 standalone，腳本會在場景 A 抓到 OperationFailure 並提示退出。
   本機要試的話，可以用單節點 replica set：
       mongod --dbpath /your/data/dir --replSet rs0
       mongosh --eval 'rs.initiate()'

對照 pgsql.try_06_transaction 的差別：
    - PG 的 transaction 是天生內建（每條連線一打開就在交易裡）；
      MongoDB 是「每筆操作天生 atomic，跨文件才需要顯式 transaction」
    - 啟動方式：client.start_session() → session.start_transaction()，
      所有要參與交易的操作都得帶上 session=session 參數
    - with start_transaction() 區塊正常結束會 commit、拋例外會 abort，
      語意跟 with psycopg.connect(...) 一致
    - MongoDB 沒有 trigger，所以這份 demo 不會看到「trigger 被一起 rollback」的觀察點。
      改用 update operator $currentDate 取代 trigger 的功能（見 try_03_update）

⭐ 觀念：MongoDB 大多數場景用 embedded document（一份文件一次寫完）就不需要 transaction，
   這也是為什麼 orders 把 order_details 嵌入後，更新訂單 + 明細根本不用交易。
"""

import sys
from typing import Any

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from mongodb.config import get_db_name, get_mongo_uri


def pick_two_latest_ids(db: Any) -> tuple[int, int]:
    docs = list(db.address_book.find({}, {"ab_id": 1}).sort("ab_id", -1).limit(2))
    if len(docs) < 2:
        sys.exit("address_book 至少要有 2 筆資料才能跑這個示範，請先執行 try_02_insert")
    return docs[0]["ab_id"], docs[1]["ab_id"]


def show_state(db: Any, ids: tuple[int, int]) -> None:
    for doc in db.address_book.find({"ab_id": {"$in": list(ids)}}).sort("ab_id", 1):
        print(f"    ab_id={doc['ab_id']}  name={doc['name']:<10}  "
              f"updated_at={doc.get('updated_at')}")


def fetch_originals(db: Any, ids: tuple[int, int]) -> dict[int, str]:
    return {
        d["ab_id"]: d["name"]
        for d in db.address_book.find({"ab_id": {"$in": list(ids)}})
    }


def main() -> None:
    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        id1, id2 = pick_two_latest_ids(db)
        print(f"使用 ab_id={id1} 與 ab_id={id2} 做示範\n")

        originals = fetch_originals(db, (id1, id2))
        print("初始狀態：")
        show_state(db, (id1, id2))

        # ---- 場景 A：交易內拋例外 → abort ----
        print("\n--- 場景 A：中途拋例外 → abort_transaction ---")
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    db.address_book.update_one(
                        {"ab_id": id1},
                        {"$set": {"name": "交易測試A"},
                         "$currentDate": {"updated_at": True}},
                        session=session,
                    )
                    print("  第 1 個 UPDATE 已送出（但還沒 commit）")
                    raise RuntimeError("故意拋例外，模擬中途失敗")
        except RuntimeError as e:
            print(f"  已捕捉例外：{e}")
            print("  → 離開 with start_transaction 區塊時自動 abort")
        except OperationFailure as e:
            # 最常見原因：連到的是 standalone mongod，不是 replica set
            print(f"\n⚠️ MongoDB 拒絕 transaction：{e}")
            print("最可能的原因：MongoDB 是 standalone 模式，不是 replica set。")
            print("見本檔開頭的設定方式。")
            return

        print("場景 A 結束後（name 應該還是初始值）：")
        show_state(db, (id1, id2))

        # ---- 場景 B：兩個 UPDATE 都成功 → commit ----
        print("\n--- 場景 B：兩個 UPDATE 都成功 → commit ---")
        with client.start_session() as session:
            with session.start_transaction():
                db.address_book.update_one(
                    {"ab_id": id1},
                    {"$set": {"name": "交易測試A"},
                     "$currentDate": {"updated_at": True}},
                    session=session,
                )
                db.address_book.update_one(
                    {"ab_id": id2},
                    {"$set": {"name": "交易測試B"},
                     "$currentDate": {"updated_at": True}},
                    session=session,
                )

        print("場景 B 結束後（兩筆 name 都被改、updated_at 也被 $currentDate 寫入）：")
        show_state(db, (id1, id2))

        # ---- 還原 ----
        # 這裡刻意不用 transaction：每次 update_one 本身就是 atomic（MongoDB
        # 對單一文件的寫入天生原子化），還原兩筆獨立資料不需要把它們綁成一個交易。
        # transaction 是為了「跨文件一致性」存在 ── 像場景 B 那樣兩筆要嘛都成功、
        # 要嘛都不動，才有意義。
        print("\n--- 還原 name 到原始值 ---")
        for ab_id, name in originals.items():
            db.address_book.update_one(
                {"ab_id": ab_id},
                {"$set": {"name": name}, "$currentDate": {"updated_at": True}},
            )
        print("還原後：")
        show_state(db, (id1, id2))


if __name__ == "__main__":
    main()
