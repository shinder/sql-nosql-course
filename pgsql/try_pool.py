"""連線池測試程式。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_pool

驗證項目：
    1. 從池中借出/歸還連線
    2. 多執行緒同時取用連線（觀察池的併發行為）
    3. 印出池統計資訊
"""

# threading 是 Python 內建的多執行緒模組，
# 用來模擬「多個請求同時想拿連線」的情況，驗證池的併發行為。
import threading
import time

from pgsql.pool import close_pool, get_pool


def run_query(worker_id: int) -> None:
    """模擬一個 worker：借連線、執行查詢、歸還。"""
    # 每個 thread 都會呼叫 get_pool()，但因為是單例，
    # 拿到的是同一個池物件（不會每個 thread 各建一個池）。
    pool = get_pool()

    # pool.connection() 從池子借出一條連線，with 結束時自動歸還回池子。
    # 如果池內所有連線都被借光，這一行會「卡住」等別的 thread 歸還。
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # pg_backend_pid() 回傳「處理這個查詢的 PostgreSQL 後端 process ID」，
            # 觀察 pid 就能看出哪幾個 worker 共用同一條連線（pid 會重複）。
            cur.execute("SELECT pg_backend_pid(), now();")

            # fetchone() 回傳 tuple，可以用「拆包 (unpacking)」一次塞給多個變數。
            pid, now = cur.fetchone()
            print(f"[worker {worker_id}] backend_pid={pid}  now={now}")

            # 故意 sleep 0.5 秒模擬「查詢很慢」，讓連線被佔用一段時間，
            # 才能觀察到後面排隊的 worker 真的有在等。
            time.sleep(0.5)


def main() -> None:
    # 第一次呼叫 get_pool() 才會真的建池子，並套用這裡傳入的 min_size / max_size。
    # 最大 5 條連線，等下故意開 8 個 worker，就會有 3 個要排隊。
    pool = get_pool(min_size=2, max_size=5)
    print(f"連線池建立完成：min={pool.min_size}, max={pool.max_size}")

    # try / finally：不管中間有沒有出錯，finally 區塊都會執行，
    # 確保 close_pool() 一定被呼叫，避免留下沒關掉的連線。
    try:
        print("\n--- 單一連線測試 ---")
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user;")
                db, user = cur.fetchone()
                print(f"已連線：database={db}, user={user}")

        print("\n--- 併發測試（8 個 worker，池上限 5）---")
        # List comprehension：等同於 for 迴圈一個個 append，但寫法更精簡。
        # 建立 8 個 Thread 物件，target 指定要執行的函式，args 是傳給該函式的參數。
        threads = [
            threading.Thread(target=run_query, args=(i,)) for i in range(1, 9)
        ]

        # perf_counter() 是高精度計時器，比 time.time() 更適合量測「經過了多久」。
        start = time.perf_counter()

        # start() 啟動 thread（開始執行 run_query），是「非阻塞」的，
        # for 迴圈會一口氣把 8 個 thread 都啟動，不會等其中一個跑完。
        for t in threads:
            t.start()

        # join() 是「阻塞」的：等該 thread 真的跑完才繼續。
        # 全部 join 過一輪 = 確認所有 thread 都結束了。
        for t in threads:
            t.join()

        elapsed = time.perf_counter() - start
        print(f"\n完成 8 個查詢耗時 {elapsed:.2f}s")
        print("（每個查詢 sleep 0.5s；上限 5 條連線 → 預期約 1.0s）")

        print("\n--- 池統計 ---")
        # get_stats() 回傳 dict，包含借出次數、等待次數、平均等待時間等指標，
        # 上線後可以拿來監控連線池有沒有設太小（等待次數高 → 應該調大 max_size）。
        stats = pool.get_stats()
        # dict.items() 同時取出 key 和 value
        for k, v in stats.items():
            print(f"  {k}: {v}")
    finally:
        close_pool()
        print("\n連線池已關閉")


if __name__ == "__main__":
    main()
