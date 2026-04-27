"""PostgreSQL 連線基本範例。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_00_connect
"""

# psycopg 是 Python 連 PostgreSQL 的官方驅動（v3 版本，注意不是舊的 psycopg2）。
import psycopg

from pgsql.config import get_conninfo


def main() -> None:
    # `with psycopg.connect(...) as conn:` 是 Python 的「context manager」語法，
    # 重點：離開 with 區塊時會「自動」幫你關閉連線（即使中途出錯也會關），
    # 不用自己 try/finally + conn.close()。
    with psycopg.connect(get_conninfo()) as conn:
        # cursor (游標) 是真正執行 SQL 的物件。一條 connection 可以開多個 cursor。
        # 同樣用 with 包住，離開區塊就自動關閉 cursor。
        with conn.cursor() as cur:
            # SELECT version() 是 PostgreSQL 的內建函式，回傳資料庫版本字串，
            # 拿來當「連線是否成功」最簡單的健康檢查。
            cur.execute("SELECT version();")

            # fetchone() 取出查詢結果的「第一列」，回傳 tuple（多欄位）或 None（沒資料）。
            # 這裡只有一欄（version），所以拿 row[0] 就好。
            row = cur.fetchone()

            # `if row else "..."` 是三元運算式 (a if cond else b)，
            # row 不是 None 才取 row[0]，避免 None[0] 直接噴 TypeError。
            print("PostgreSQL 版本：", row[0] if row else "(無回應)")


# Python 慣例：`if __name__ == "__main__":` 包住的程式碼，
# 只在「直接執行這支檔案」時才會跑；被別人 import 時不會執行。
# 這樣 main() 可以重複利用，也能單獨跑這支檔案測試。
if __name__ == "__main__":
    main()
