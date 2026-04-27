"""示範交易 (transaction) 的原子性：兩個 UPDATE 要嘛都成功、要嘛都不算。

順便示範 transaction × trigger 的互動：
    address_book 上有 BEFORE UPDATE trigger 自動更新 updated_at，
    rollback 會把 trigger 寫進去的 updated_at 也一起取消（因為 trigger
    是在 transaction 內執行的，沒有特殊地位）。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_06_transaction

劇本：
    1. 自動挑出 address_book 最新兩筆當實驗對象
    2. 場景 A：第一個 UPDATE 跑完後故意拋例外 → 連線會 rollback
       → 重新查詢時，第一個 UPDATE 也「沒有發生過」（連 trigger 寫的 updated_at 都沒變）
    3. 場景 B：兩個 UPDATE 都正常跑完 → 連線正常結束 → commit
       → 重新查詢時，兩筆都被改了（updated_at 也被 trigger 自動更新）
    4. 還原 name；updated_at 因為 trigger 又會被觸發，所以無法完美還原（這也是個觀察點）

關鍵觀念：
    - psycopg 預設是「手動交易模式」（autocommit=False）
    - `with psycopg.connect(...) as conn:` 區塊正常結束會 commit、
      區塊內拋例外會 rollback ── 不用自己呼叫 conn.commit() / conn.rollback()
    - Trigger 寫入的資料也是 transaction 的一部分，rollback 會一起被取消
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
    # 至少要兩筆才能演示，否則先提醒使用者去跑 try_02_insert.py 灌資料。
    if len(rows) < 2:
        sys.exit("address_book 至少要有 2 筆資料才能跑這個示範，請先執行 try_02_insert.py")
    # rows 是 [(id1,), (id2,)] 結構，row[0] 取 tuple 裡的第一欄。
    return rows[0][0], rows[1][0]


def show_state(ids: tuple[int, int]) -> None:
    """從 DB 重新查兩筆的當前 name 與 updated_at，印出來。

    特別重新開連線查詢，是為了確認看到的是「資料庫真正的狀態」，
    而不是上一段程式記憶體裡的舊值。同時也能看到 trigger 是否真的觸發。
    """
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            # IN (%s, %s)：每個 %s 對應 execute() 第二個參數 tuple 裡的一個值，
            # 順序一一對應（這裡剛好兩個 %s 對 ids 的兩個元素）。
            cur.execute(
                "SELECT ab_id, name, updated_at FROM address_book "
                "WHERE ab_id IN (%s, %s) ORDER BY ab_id",
                ids,
            )
            for ab_id, name, updated_at in cur.fetchall():
                print(f"    ab_id={ab_id}  name={name:<10}  updated_at={updated_at}")


def fetch_original_names(ids: tuple[int, int]) -> dict[int, str]:
    """先記下原始 name，最後才還原得回去。

    回傳 dict：{ab_id: name}，這樣不必擔心兩個 id 的順序。
    （updated_at 不記，因為 trigger 會強制覆寫，記了也還原不了。）
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
                # 此時在 transaction 內：name 變了，trigger 也已經把 updated_at 設成 NOW()
                # ── 但這些變更還在 transaction buffer 裡，外面看不到。
                print("  第 1 個 UPDATE 已送出（但還沒 commit；trigger 也已觸發）")

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
        print("  → 離開 with 區塊時 psycopg 自動 rollback")
        print("  → 第 1 個 UPDATE 跟 trigger 寫的 updated_at 一起被取消")

    print("場景 A 結束後（name 跟 updated_at 都應該維持初始值）：")
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
    # with 區塊正常結束 → 自動 commit。
    # 我們的 SQL 完全沒碰 updated_at，但 trigger 會幫每筆 UPDATE 自動更新。
    #
    # 觀察點：執行下面 show_state() 時會看到兩筆的 updated_at 「一模一樣」
    # （連微秒都同步）。這不是巧合 ── PostgreSQL 的 CURRENT_TIMESTAMP / NOW()
    # 回傳的是「當前 transaction 的開始時間」，不是真正的 wall-clock。
    # 同一個 transaction 裡呼叫幾百次 NOW() 都會得到同一個值。
    # 想要每次取真正的當下時間，要用 clock_timestamp()。
    print("場景 B 結束後（name 被改、updated_at 被 trigger 自動跳到當下）：")
    show_state((id1, id2))

    # ---- 還原 ----
    print("\n--- 還原 name 到原始值 ---")
    with psycopg.connect(CONNINFO) as conn:
        with conn.cursor() as cur:
            for ab_id, original_name in originals.items():
                cur.execute(
                    "UPDATE address_book SET name = %s WHERE ab_id = %s",
                    (original_name, ab_id),
                )
    # 注意：name 還原回去了，但 updated_at 又被 trigger 設成「現在」。
    # 「還原 updated_at」其實做不到 ── 即使 SQL 寫 SET updated_at = '原值'，
    # trigger 也會在 BEFORE UPDATE 階段把 NEW.updated_at 強制覆蓋掉。
    # 這是 trigger 設計上的選擇：保證「沒人能繞過 updated_at」。
    print("還原後（name 恢復；updated_at 是這次還原 UPDATE 的時間，無法回到初始值）：")
    show_state((id1, id2))


if __name__ == "__main__":
    main()
