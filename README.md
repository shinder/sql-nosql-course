# sql-nosql

PostgreSQL 與 MongoDB 的連線與操作練習專案，定位為**教學用範例集**。
所有範例使用 [`uv`](https://docs.astral.sh/uv/) 管理 Python 環境，
SQL 端用 [`psycopg`](https://www.psycopg.org/) v3、NoSQL 端用 [`pymongo`](https://pymongo.readthedocs.io/)。

## 涵蓋主題

兩個資料庫採「**同題對照**」設計：每支 `try_NN_*.py` 都有 PG 版與 Mongo 版實作同樣的功能，
docstring 內標出兩邊的關鍵差異。涵蓋連線、CRUD、JOIN（vs `$lookup` / embedded）、
Transaction、Connection Pool。

詳細說明：

- [`pgsql/README.md`](pgsql/README.md) — PostgreSQL 端
- [`mongodb/README.md`](mongodb/README.md) — MongoDB 端

## 環境需求

- Python 3.12+ 與 [uv](https://docs.astral.sh/uv/)
- 本機 PostgreSQL 16+（建議 17）
- 本機 MongoDB 6+（建議 8.x），加上 `mongoimport`（隨 MongoDB Database Tools 安裝）
- macOS / Linux / Windows 皆可（範例以 macOS Homebrew + uv 撰寫）

> Transaction 範例需要 MongoDB 為 **replica set**（standalone 不支援）。
> 不跑 `try_06_transaction.py` 的話 standalone 也夠用。

## 快速開始

```bash
# 1. 安裝相依套件
uv sync

# 2-A. PostgreSQL：建立帳號與資料庫並匯入 schema
#      詳細步驟見 pgsql/README.md「建立帳號與資料庫」章節

# 2-B. MongoDB：把 NDJSON seed data 匯入 shin03 database
#      詳細步驟見 mongodb/README.md「匯入」章節
for col in members address_book categories products orders; do
  mongoimport --db=shin03 --collection="$col" --drop \
              --file="data/shin03-mongo/${col}.ndjson"
done

# 3. 設定連線資訊
cp .env.example .env
# 編輯 .env 填入 PGUSER / PGPASSWORD / PGDATABASE / MONGO_URI 等

# 4. 跑第一個範例驗證連線
uv run python -m pgsql.try_00_connect
uv run python -m mongodb.try_00_connect
```

## 學習順序

兩邊的 `try_NN_*.py` 編號**一一對應**，建議搭配對照閱讀：

| #  | 主題                       | PostgreSQL                  | MongoDB                       |
| -- | -------------------------- | --------------------------- | ----------------------------- |
| 00 | 連線測試                   | `pgsql/try_00_connect.py`   | `mongodb/try_00_connect.py`   |
| 01 | SELECT / find              | `pgsql/try_01_select.py`    | `mongodb/try_01_select.py`    |
| 02 | INSERT（含 Faker）         | `pgsql/try_02_insert.py`    | `mongodb/try_02_insert.py`    |
| 03 | UPDATE（trigger / `$currentDate`） | `pgsql/try_03_update.py` | `mongodb/try_03_update.py` |
| 04 | DELETE                     | `pgsql/try_04_delete.py`    | `mongodb/try_04_delete.py`    |
| 05 | JOIN（vs `$lookup` / embed）| `pgsql/try_05_join.py`     | `mongodb/try_05_join.py`      |
| 06 | Transaction                | `pgsql/try_06_transaction.py` | `mongodb/try_06_transaction.py` |
| 07 | Connection Pool            | `pgsql/try_07_pool.py`      | `mongodb/try_07_pool.py`      |

每支腳本都附詳細中文註解，假設讀者只有基本 Python 知識。
Mongo 版的 docstring 開頭都會列出「對照 pgsql.try_NN_xxx 的差別」。

## 資料來源

- `data/shin02-pgsql.sql` — PostgreSQL 的 schema + seed（從 `data/shin02-mysql.sql` 改寫而來）
- `data/shin03-mongo/*.ndjson` — MongoDB 的 seed，由 `mongodb/export_to_ndjson.py` 從 PG 端匯出

## 安全注意事項

- 範例使用的預設密碼（如 `pgUser567`）**僅供本機練習**；切勿沿用於可被外網存取的 DB。
- `.env` 已被 `.gitignore` 排除，請確認你的真實密碼不會誤 commit。
- seed data 中的姓名 / email / 手機皆為生成的假資料。

## 授權

MIT License — 詳見 [LICENSE](LICENSE)
