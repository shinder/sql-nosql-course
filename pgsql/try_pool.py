"""連線池測試程式。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_pool

驗證項目：
    1. 從池中借出/歸還連線
    2. 多執行緒同時取用連線（觀察池的併發行為）
    3. 印出池統計資訊
"""

import threading
import time

from pgsql.pool import close_pool, get_pool


def run_query(worker_id: int) -> None:
    """模擬一個 worker：借連線、執行查詢、歸還。"""
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_backend_pid(), now();")
            pid, now = cur.fetchone()
            print(f"[worker {worker_id}] backend_pid={pid}  now={now}")
            time.sleep(0.5)


def main() -> None:
    pool = get_pool(min_size=2, max_size=5)
    print(f"連線池建立完成：min={pool.min_size}, max={pool.max_size}")

    try:
        print("\n--- 單一連線測試 ---")
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user;")
                db, user = cur.fetchone()
                print(f"已連線：database={db}, user={user}")

        print("\n--- 併發測試（8 個 worker，池上限 5）---")
        threads = [
            threading.Thread(target=run_query, args=(i,)) for i in range(1, 9)
        ]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start
        print(f"\n完成 8 個查詢耗時 {elapsed:.2f}s")
        print("（每個查詢 sleep 0.5s；上限 5 條連線 → 預期約 1.0s）")

        print("\n--- 池統計 ---")
        stats = pool.get_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")
    finally:
        close_pool()
        print("\n連線池已關閉")


if __name__ == "__main__":
    main()
