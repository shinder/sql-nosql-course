"""連線池測試 ── 對照 pgsql.try_07_pool。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_07_pool

🌟 重點：MongoClient 本身就是連線池！
   不需要額外的 pool wrapper（pgsql 的範例用 psycopg-pool 包了一層）。
   建立 MongoClient(uri) 後內部就維護一個 socket pool；任何 db.collection.xxx()
   呼叫都會從池借一條 socket 用、操作結束立刻歸還。

對照 pgsql.try_07_pool 的差別：
    - psycopg：with conn 區塊期間「占住」一條連線，包進 sleep 連線就被卡死
    - pymongo：每筆操作執行的瞬間借 socket，操作結束立刻歸還；
              應用層不直接持有連線，pool 完全由 driver 管理
    → 你不太需要關心 maxPoolSize 該設多少，預設 100 通常就夠用，
      除非真的很多執行緒同時跑「長查詢」。

可調的池參數（建立 MongoClient 時傳入）：
    maxPoolSize           池內最多開幾條連線（預設 100）
    minPoolSize           池內最少保留幾條連線（預設 0）
    waitQueueTimeoutMS    借不到連線最多等幾毫秒（預設 0 = 無限等）

慣例：每個 process 只建一個 MongoClient 全程共用，不要每次操作都 new 一個 ──
新建 client 要做 SDAM topology discovery、TLS handshake 等，成本不低。
"""

import threading
import time

from pymongo import MongoClient

from mongodb.config import get_db_name, get_mongo_uri

WORKERS = 8


def run_query(client: MongoClient, worker_id: int) -> None:
    """每個 worker 都透過共用的 client 操作；socket 借還由 driver 自動處理。"""
    db = client[get_db_name()]
    # 用簡單查詢練習 ── pymongo 內部自動從池借 / 還 socket，外部看不到也不用管
    doc = db.address_book.find_one({"ab_id": worker_id})
    name = doc["name"] if doc else "(無)"
    print(f"[worker {worker_id}] 查到 ab_id={worker_id} → {name}")


def main() -> None:
    # 故意設小 maxPoolSize 觀察池參數；正式專案幾乎不用調，預設就好。
    client = MongoClient(get_mongo_uri(), maxPoolSize=5, minPoolSize=2)
    try:
        info = client.server_info()
        print(f"MongoDB 版本：{info['version']}")
        # ClientOptions 內可看到當下生效的池設定
        pool_opts = client.options.pool_options
        print(f"maxPoolSize={pool_opts.max_pool_size}, "
              f"minPoolSize={pool_opts.min_pool_size}")

        print(f"\n--- 併發測試（{WORKERS} 個 thread 共用同一個 MongoClient）---")
        threads = [
            threading.Thread(target=run_query, args=(client, i))
            for i in range(1, WORKERS + 1)
        ]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start
        print(f"\n{WORKERS} 個查詢耗時 {elapsed:.3f}s")
        print("（pymongo 自動 reuse pool 內 socket，不會每次都新開）")

        # 從 server 端看 client 實際開了幾條連線
        print("\n--- Server 端 connection 統計（serverStatus.connections）---")
        conns = client.admin.command("serverStatus").get("connections", {})
        for k in ("current", "active", "available", "totalCreated"):
            if k in conns:
                print(f"  {k}: {conns[k]}")
        print("\ntotalCreated 是 server 自啟動以來建立過的 socket 累計數；")
        print("跑完這支腳本後再跑一次，可以看出 pymongo 在程式內 reuse 同一批 socket。")
    finally:
        client.close()
        print("\nMongoClient 已關閉")


if __name__ == "__main__":
    main()
