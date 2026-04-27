"""示範交易 (transaction) 的原子性：兩個 UPDATE 要嘛都成功、要嘛都不算。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_06_transaction

劇本：
    1. 自動挑出 address_book 最新兩筆當實驗對象
    2. 場景 A：第一個 UPDATE 跑完後故意拋例外 → 連線會 rollback
       → 重新查詢時，第一個 UPDATE 也「沒有發生過」
    3. 場景 B：兩個 UPDATE 都正常跑完 → 連線正常結束 → commit
       → 重新查詢時，兩筆都被改了
    4. 還原成原始資料，避免反覆執行把資料弄亂

關鍵觀念：
    - psycopg 預設是「手動交易模式」（autocommit=False）
    - `with psycopg.connect(...) as conn:` 區塊正常結束會 commit、
      區塊內拋例外會 rollback ── 不用自己呼叫 conn.commit() / conn.rollback()
    - 想要明確控制的話，也可以用：
          conn = psycopg.connect(...)
          try:
              ... cur.execute ...
              conn.commit()
          except Exception:
              conn.rollback()
              raise
          finally:
              conn.close()
"""

import sys

import psycopg

from pgsql.config import get_conninfo

# 模組層級先把 conninfo 算好，下面多個函式都會用到，免得每次都重新讀 .env。
CONNINFO = get_conninfo()


def pick_two_latest_ids() -> tuple[int, int]:
    """挑 address_book 最新的兩個 ab_id 當實驗對象。"""
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ab_id FROM address_book ORDER BY ab_id DESC LIMIT 2")
            rows = cur.fetchall()
    # 至少要兩筆才能演示，否則先提醒使用者去跑 run_insert.py 灌資料。
    if len(rows) < 2:
        sys.exit("address_book 至少要有 2 筆資料才能跑這個示範，請先執行 run_insert.py")
    # rows 是 [(id1,), (id2,)] 結構，row[0] 取 tuple 裡的第一欄。
    return rows[0][0], rows[1][0]


def show_state(ids: tuple[int, int]) -> None:
    """從 DB 重新查兩筆的當前 name，印出來。

    特別重新開連線查詢，是為了確認看到的是「資料庫真正的狀態」，
    而不是上一段程式記憶體裡的舊值。
    """
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            # IN (%s, %s)：每個 %s 對應 execute() 第二個參數 tuple 裡的一個值，
            # 順序一一對應（這裡剛好兩個 %s 對 ids 的兩個元素）。
            cur.execute(
                "SELECT ab_id, name FROM address_book WHERE ab_id IN (%s, %s) ORDER BY ab_id",
                ids,
            )
            for ab_id, name in cur.fetchall():
                print(f"    ab_id={ab_id}  name={name}")


def fetch_original_names(ids: tuple[int, int]) -> dict[int, str]:
    """先記下原始 name，最後才還原得回去。

    回傳 dict：{ab_id: name}，這樣不必擔心兩個 id 的順序。
    """
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ab_id, name FROM address_book WHERE ab_id IN (%s, %s)",
                ids,
            )
            # dict comprehension：把 [(id, name), ...] 變成 {id: name, ...}
            return {ab_id: name for ab_id, name in cur.fetchall()}


def main() -> None:
    id1, id2 = pick_two_latest_ids()
    print(f"使用 ab_id={id1} 與 ab_id={id2} 做示範\n")

    originals = fetch_original_names((id1, id2))

    print("初始狀態：")
    show_state((id1, id2))

    # ---- 場景 A：中途拋例外，整個 transaction 被 rollback ----
    print("\n--- 場景 A：中途拋例外 → rollback ---")
    try:
        with psycopg.connect(CONNINFO) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE address_book SET name = %s WHERE ab_id = %s",
                    ("交易測試A", id1),
                )
                print("  第 1 個 UPDATE 已送出（但還沒 commit）")

                # 故意拋例外模擬「中途出狀況」（實務上可能是業務邏輯檢查失敗、
                # 第二個 UPDATE 違反約束、外部 API 連線失敗等等）。
                raise RuntimeError("故意拋例外，模擬中途失敗")

                # 下面這一行根本不會執行，只是讓劇本完整。
                cur.execute(
                    "UPDATE address_book SET name = %s WHERE ab_id = %s",
                    ("交易測試B", id2),
                )
    except RuntimeError as e:
        # 例外傳出 with 區塊時，psycopg 會自動 rollback，
        # 連線也會被關閉。我們只需要在外面接住例外避免程式中斷。
        print(f"  已捕捉例外：{e}")
        print("  → 離開 with 區塊時 psycopg 自動 rollback，第 1 個 UPDATE 也被取消")

    print("場景 A 結束後（兩筆應該都還是原本的 name）：")
    show_state((id1, id2))

    # ---- 場景 B：全部成功，整個 transaction 被 commit ----
    print("\n--- 場景 B：兩個 UPDATE 都成功 → commit ---")
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE address_book SET name = %s WHERE ab_id = %s",
                ("交易測試A", id1),
            )
            cur.execute(
                "UPDATE address_book SET name = %s WHERE ab_id = %s",
                ("交易測試B", id2),
            )
    # with 區塊正常結束 → 自動 commit
    print("場景 B 結束後（兩筆 name 都被改了）：")
    show_state((id1, id2))

    # ---- 還原 ----
    print("\n--- 還原原始 name，讓資料庫回到實驗前的狀態 ---")
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            for ab_id, original_name in originals.items():
                cur.execute(
                    "UPDATE address_book SET name = %s WHERE ab_id = %s",
                    (original_name, ab_id),
                )
    print("還原後：")
    show_state((id1, id2))


if __name__ == "__main__":
    main()
