"""示範 MongoDB 怎麼處理「跨集合關聯」── 對照 pgsql.try_05_join 的 INNER/LEFT JOIN。

執行方式（從專案根目錄）：
    uv run python -m mongodb.try_05_join

⭐ 這支是 SQL 思維 vs MongoDB 思維最大的對比。

對照 pgsql.try_05_join 的差別：
    1. orders.details 是 embedded array（在 export_to_ndjson 時把 order_details 嵌入）。
       查訂單明細不需要 JOIN，直接讀陣列就好。
       這是 MongoDB 的 schema 設計信條：「會一起讀的就放一起 (embed)」。
    2. 跨集合關聯（如「訂單對應的會員」）用 aggregation pipeline 的 $lookup 階段，
       概念類似 LEFT JOIN：左邊全部保留，找不到對應就空陣列。
    3. 沒有 INNER JOIN 直接對應 ── 用 $lookup 後再 $match 過濾掉空陣列即可。
"""

from pymongo import MongoClient

from mongodb.config import get_db_name, get_mongo_uri


def section(title: str) -> None:
    print(f"\n--- {title} ---")


def print_rows(rows: list[dict]) -> None:
    if not rows:
        print("  (沒有資料)")
        return
    headers = list(rows[0].keys())
    print("  " + " | ".join(headers))
    print("  " + "-+-".join("-" * len(h) for h in headers))
    for row in rows:
        print("  " + " | ".join(str(row[h]) for h in headers))


def main() -> None:
    with MongoClient(get_mongo_uri()) as client:
        db = client[get_db_name()]

        # ─────────────────────────────────────────────
        # 範例 1：embedded document — JOIN 在 schema 設計時就解決了
        # 訂單明細在 orders.details 陣列裡，根本不用 JOIN。
        # ─────────────────────────────────────────────
        section("Embedded：列出每筆訂單與其明細（不用 JOIN）")
        # 第二參數是 projection：1 表示要、0 表示不要。
        # 對應 SQL 的 SELECT col1, col2 FROM ...
        orders = list(db.orders.find(
            {},
            {"_id": 0, "order_id": 1, "amount": 1, "details": 1},
        ))
        for o in orders:
            print(f"  order_id={o['order_id']}  amount={o['amount']}")
            for d in o["details"]:
                print(f"    └ od_id={d['od_id']}  product_id={d['product_id']}  "
                      f"price={d['price']}  qty={d['quantity']}")
        print("\n關鍵：details 是文件內的子陣列，沒有跨集合查詢。")
        print("換成 PG 的 schema 寫，這個結果要 JOIN orders × order_details。")

        # ─────────────────────────────────────────────
        # 範例 2：$lookup（aggregation） — 對應 LEFT JOIN
        # 用 members 當左邊，把對應的 orders 集合進每位會員下的 orders 陣列。
        # 沒下單的會員 orders 會是空陣列（對應 LEFT JOIN 沒對到時的 NULL）。
        # ─────────────────────────────────────────────
        section("$lookup：每位會員的訂單數（對應 LEFT JOIN + COUNT）")
        pipeline = [
            {"$lookup": {
                "from": "orders",            # 要 join 的目標集合
                "localField": "member_id",   # 左邊（members）的欄位
                "foreignField": "member_id", # 右邊（orders）的欄位
                "as": "orders",              # 結果放在這個欄位（陣列）
            }},
            {"$project": {
                "_id": 0,
                "member_id": 1,
                "nickname": 1,
                "order_count": {"$size": "$orders"},  # 算陣列長度，等同 COUNT
            }},
            {"$sort": {"member_id": 1}},
        ]
        rows = list(db.members.aggregate(pipeline))
        print_rows(rows)
        print("\n觀察點：『瑪麗亞』(member_id=8) 沒下過單，order_count=0 仍會出現。")
        print("$lookup 預設行為就是 LEFT JOIN ── 跟 SQL 預設 INNER 不同。")

        # ─────────────────────────────────────────────
        # 範例 3：多 stage pipeline — 對應 4 表 JOIN
        # orders → $lookup members（買家）→ $unwind details → $lookup products（書名）
        # 這是 aggregation 的核心模式：用一連串 stage 串成資料管線。
        # ─────────────────────────────────────────────
        section("多 stage pipeline：訂單明細含會員 + 書名 + 小計")
        pipeline = [
            {"$lookup": {
                "from": "members",
                "localField": "member_id",
                "foreignField": "member_id",
                "as": "member",
            }},
            {"$unwind": "$member"},          # member 是陣列（一筆訂單一個會員），攤成單一物件
            {"$unwind": "$details"},         # details 陣列每元素變一行（像 JOIN 把多筆攤開）
            {"$lookup": {
                "from": "products",
                "localField": "details.product_id",
                "foreignField": "product_id",
                "as": "product",
            }},
            {"$unwind": "$product"},
            {"$project": {
                "_id": 0,
                "nickname": "$member.nickname",
                "order_id": 1,
                "book_name": "$product.book_name",
                "quantity": "$details.quantity",
                "price": "$details.price",
                "subtotal": {"$multiply": ["$details.price", "$details.quantity"]},
            }},
            {"$sort": {"order_id": 1}},
        ]
        rows = list(db.orders.aggregate(pipeline))
        print_rows(rows)
        print("\n觀察點：")
        print("- $unwind 把陣列『攤開』，每元素變一行 ── 跟 SQL JOIN 多筆攤開類似。")
        print("- $project 用 $multiply 算 subtotal，相當於 SQL 的 price * quantity AS subtotal。")
        print("- aggregation pipeline 是 MongoDB 表達複雜查詢的核心模式 ── 你會看到")
        print("  $match / $group / $project / $lookup / $unwind 一直被組合使用。")


if __name__ == "__main__":
    main()
