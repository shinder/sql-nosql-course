"""MongoDB 連線基本範例。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_00_connect

預期輸出：
    MongoDB 版本：       8.x.x
    使用 database：      shin03
    現有 collections：   ['address_book', 'categories', 'members', 'orders', 'products']
"""

# pymongo 是 MongoDB 官方提供的 Python 同步 driver。
# 如果以後要改成 async（搭 FastAPI / asyncio），可以換成 motor 或 pymongo 內建的 AsyncMongoClient。
from pymongo import MongoClient

from mongodb.config import get_db_name, get_mongo_uri


def main() -> None:
    # MongoClient 建立時不會立刻連線（lazy），第一次發出指令才會真的去連。
    # 用 with 包住 → 離開區塊時自動 client.close()，跟 psycopg.connect 的用法一致。
    with MongoClient(get_mongo_uri()) as client:
        # client.server_info() 是最簡單的「連線是否成功」健康檢查 ──
        # 它呼叫 MongoDB 的 buildInfo command，回傳 dict，連不上會直接拋 ServerSelectionTimeoutError。
        info = client.server_info()
        print(f"MongoDB 版本：     {info['version']}")

        # client[name] 取得 Database 物件；MongoDB 的 database / collection 都是「用到時才存在」，
        # 所以這行不會建立任何東西，只是拿到一個操作的 handle。
        db = client[get_db_name()]
        print(f"使用 database：    {db.name}")

        # 列出目前 database 內已有的 collection 名稱。
        # 還沒匯入資料前會是 []，跑過 mongoimport（見 mongodb/README.md）後就會看到 5 個。
        print(f"現有 collections： {db.list_collection_names()}")


if __name__ == "__main__":
    main()
