"""把 PostgreSQL shin02 資料庫的每張表匯出成 NDJSON 檔，供 mongoimport 使用。

每張表會輸出一個 `<table>.ndjson` 檔（Newline-Delimited JSON：一行一個
document），存放在 `data/shin02-mongo/` 底下。日期 / 時間欄位用 MongoDB
Extended JSON `{"$date": "..."}` 表達，這樣 mongoimport 進去會是
BSON Date 型別而非字串，方便後續日期區間查詢。

副檔名選 `.ndjson` 而不是 `.json`，是因為內容並非合法的單一 JSON 值
（每行才是），用 `.json` 會讓編輯器 / `jq` 等工具誤判失敗。

執行方式（從專案根目錄）：

    uv run python -m mongodb.export_to_ndjson

匯入到 MongoDB：

    for col in members address_book categories products orders \
               order_details ab_likes hobby users post; do
      mongoimport --db=shin02 --collection="$col" \
                  --file="data/shin02-mongo/${col}.ndjson"
    done
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from pgsql.config import get_conninfo


# 依外鍵相依順序排列（雖然 mongoimport 不在意順序，但讀起來比較直覺）
TABLES: list[str] = [
    "members",
    "address_book",
    "categories",
    "products",
    "orders",
    "order_details",
    "ab_likes",
    "hobby",
    "users",
    "post",
]


def _to_extjson(obj: object) -> object:
    """JSON 編碼器的 fallback：把 date / datetime 轉成 MongoDB Extended JSON。

    PostgreSQL 的 TIMESTAMP（沒帶 time zone）由 psycopg 回傳為 naive datetime，
    這裡一律當成 UTC 處理（補上 Z）。實務上若資料庫存的是當地時間，
    匯入後在 MongoDB 看到的時間會偏移 — 教學情境可接受。
    """
    if isinstance(obj, datetime):
        return {"$date": obj.isoformat(timespec="milliseconds") + "Z"}
    if isinstance(obj, date):
        # MongoDB 沒有純 DATE 型別；補上午夜時間並標 UTC
        return {"$date": f"{obj.isoformat()}T00:00:00.000Z"}
    raise TypeError(f"不支援的型別：{type(obj).__name__}")


def export_table(conn: psycopg.Connection, table: str, out_dir: Path) -> int:
    """把單一資料表匯出為 JSONL 檔，回傳寫出的筆數。"""
    query = sql.SQL("SELECT * FROM {} ORDER BY 1").format(sql.Identifier(table))
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    out_path = out_dir / f"{table}.ndjson"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=_to_extjson) + "\n")
    return len(rows)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    out_dir = project_root / "data" / "shin02-mongo"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"連線到 PostgreSQL，輸出到：{out_dir}\n")
    with psycopg.connect(get_conninfo()) as conn:
        total = 0
        for table in TABLES:
            count = export_table(conn, table, out_dir)
            total += count
            print(f"  {table:<14} -> {count:>4} 筆")
    print(f"\n完成，共 {total} 筆資料寫入 {len(TABLES)} 個檔案。")


if __name__ == "__main__":
    main()
