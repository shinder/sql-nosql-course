"""示範 INNER JOIN 與 LEFT JOIN 的差別，再加一個多表 JOIN 範例。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_join

用到的表：
    members         會員（member_id 是 PK）
    orders          訂單（FK: member_id → members）
    order_details   訂單明細（FK: order_id → orders；FK: product_id → products）
    products        商品（product_id 是 PK）

seed 資料剛好有個會員「瑪麗亞」沒下過任何訂單，
正好用來凸顯 INNER JOIN 跟 LEFT JOIN 的差別。
"""

import psycopg
from psycopg.rows import dict_row

from pgsql.config import get_conninfo


def section(title: str) -> None:
    """印出區塊標題，純粹排版用。"""
    print(f"\n--- {title} ---")


def run(sql: str) -> list[dict]:
    """跑一個 SELECT 並回傳 list of dict。範例用，所以共用一條短連線。"""
    with psycopg.connect(get_conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def print_rows(rows: list[dict]) -> None:
    """把 list of dict 印成簡單表格。沒資料就提示一下。"""
    if not rows:
        print("  (沒有資料)")
        return
    # 取第一列的 key 當欄位名（所有列的 key 都一樣，因為來自同一個 SELECT）
    headers = list(rows[0].keys())
    print("  " + " | ".join(headers))
    print("  " + "-+-".join("-" * len(h) for h in headers))
    for row in rows:
        # str(...) 是因為值可能是 int / datetime / None 等不同型別
        print("  " + " | ".join(str(row[h]) for h in headers))


def main() -> None:
    # ─────────────────────────────────────────────
    # 範例 1：INNER JOIN
    # 「兩邊都要有對應資料」才會出現在結果裡。
    # 沒下單的會員不會出現；沒對應會員的訂單也不會出現（這裡不會發生，因為有 FK）。
    # ─────────────────────────────────────────────
    section("INNER JOIN：列出每筆訂單與下單會員")
    rows = run("""
        SELECT
            o.order_id,
            m.nickname,
            o.amount,
            o.ordered_at
        FROM orders o
        INNER JOIN members m ON o.member_id = m.member_id
        ORDER BY o.ordered_at
    """)
    print_rows(rows)
    # 注意：表別名 (alias) `o` 跟 `m` 是 SQL 寫長 JOIN 時的常用技巧，
    # 等同於 `FROM orders AS o`，AS 可以省略。後面引用欄位就能寫 `o.order_id`。

    # ─────────────────────────────────────────────
    # 範例 2：LEFT JOIN
    # 「左邊一定保留」，右邊沒對應就用 NULL 補。
    # 這裡左邊是 members → 沒下過單的會員也會出現，order_count 會是 0。
    # ─────────────────────────────────────────────
    section("LEFT JOIN：列出所有會員與其訂單數（沒下單的也要出現）")
    rows = run("""
        SELECT
            m.member_id,
            m.nickname,
            COUNT(o.order_id) AS order_count
        FROM members m
        LEFT JOIN orders o ON m.member_id = o.member_id
        GROUP BY m.member_id, m.nickname
        ORDER BY m.member_id
    """)
    print_rows(rows)
    # 觀察點：用 INNER JOIN 改寫的話，「瑪麗亞」(沒下過單) 就會消失。
    # 為什麼 COUNT 是 COUNT(o.order_id) 而不是 COUNT(*)？
    # 因為 LEFT JOIN 後沒對應的列會用 NULL 補 o.order_id，
    # COUNT(欄位) 會跳過 NULL → 沒下單的會員會得到 0；COUNT(*) 會算成 1。

    # ─────────────────────────────────────────────
    # 範例 3：多表 JOIN（4 張表）
    # 訂單 → 會員（誰買的）→ 訂單明細（買了什麼項目）→ 商品（書名）
    # 這就是電商常見的「訂單明細查詢」雛形。
    # ─────────────────────────────────────────────
    section("多表 JOIN：每筆訂單明細的會員 + 書名 + 小計")
    rows = run("""
        SELECT
            m.nickname,
            o.order_id,
            p.book_name,
            od.quantity,
            od.price,
            od.price * od.quantity AS subtotal
        FROM orders o
        JOIN members m       ON o.member_id = m.member_id
        JOIN order_details od ON o.order_id = od.order_id
        JOIN products p      ON od.product_id = p.product_id
        ORDER BY o.order_id, od.od_id
    """)
    print_rows(rows)
    # 注意：JOIN 不寫 INNER 預設就是 INNER JOIN（兩種寫法等價）。
    # 寫 ORM (如 SQLAlchemy) 之前先把這種純 SQL 的 JOIN 練熟，
    # 之後看 ORM 產生的 SQL 才知道在做什麼。


if __name__ == "__main__":
    main()
