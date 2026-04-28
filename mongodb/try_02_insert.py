"""產生隨機資料並批次寫入 address_book collection。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_02_insert         # 預設新增 5 筆
    uv run python -m mongodb.try_02_insert 50      # 指定筆數（上限 100）

對照 pgsql.try_02_insert 的差別：
    - 直接塞 dict，不寫 INSERT SQL，不用列欄位順序
    - 沒有 schema → 想加新欄位直接加，不必 ALTER TABLE / 改 migration
    - 沒有 SERIAL 自動編號的整數 PK → MongoDB 預設用 ObjectId 當 _id
      （12 bytes：時間戳 + machine ID + 隨機值，跨機器幾乎不會重複）
    - 為了和從 PG 匯入的舊資料對齊，這裡仍維持整數 ab_id 欄位，
      用 max(ab_id)+1 手動續號 ── 註：高併發下不安全，
      正式環境會用 Counter 文件 + findOneAndUpdate atomic 取號
"""

import random
import sys
from datetime import datetime

from faker import Faker
from pymongo import MongoClient

from mongodb.config import get_db_name, get_mongo_uri

fake = Faker("zh_TW")
DEFAULT_ROWS = 5
MAX_ROWS = 100

CITIES = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "嘉義市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣",
    "澎湖縣", "金門縣", "連江縣",
]


def make_doc(ab_id: int) -> dict:
    """產生一筆假資料的 dict。對照 PG 版回傳 tuple，差別在於欄位是 key 而非位置。"""
    return {
        "ab_id": ab_id,
        "name": fake.name(),
        "email": fake.email(),
        "mobile": "09" + "".join(random.choices("0123456789", k=8)),
        # MongoDB 沒有純 DATE 型別，全部用 BSON Date（含時分秒）。
        # Faker 給 date，這裡 pad 成 datetime（午夜 0 點）。
        "birthday": datetime.combine(
            fake.date_of_birth(minimum_age=20, maximum_age=60),
            datetime.min.time(),
        ),
        "address": random.choice(CITIES),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROWS
    if n > MAX_ROWS:
        sys.exit(f"筆數最多 {MAX_ROWS}（指定為 {n}）")
    if n < 1:
        sys.exit(f"筆數需大於 0（指定為 {n}）")

    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        # 找目前最大 ab_id 當基準。find_one + sort + limit(1) 的組合。
        # find_one 直接傳 sort 參數比 .sort().limit(1) 更短；
        # 沒資料時回傳 None。
        last = db.address_book.find_one({}, sort=[("ab_id", -1)])
        next_id = (last["ab_id"] + 1) if last else 1

        docs = [make_doc(next_id + i) for i in range(n)]

        # insert_many：一次 round trip 塞多筆，比迴圈呼叫 insert_one 快得多。
        # 回傳 InsertManyResult；inserted_ids 是 ObjectId 的 list（不是我們的 ab_id），
        # 因為 _id 預設由 MongoDB 自己生。
        result = db.address_book.insert_many(docs)

    print(f"已新增 {len(result.inserted_ids)} 筆，ab_id 範圍：{next_id} ~ {next_id + n - 1}")
    print(f"前 3 筆 _id (ObjectId)：")
    for oid in result.inserted_ids[:3]:
        print(f"  {oid}")
    print("\n前 3 筆樣本：")
    for doc in docs[:3]:
        print(f"  {doc}")


if __name__ == "__main__":
    main()
