# sql-nosql

PostgreSQL（未來預計擴及 NoSQL）連線與操作練習專案，定位為**教學用範例集**。
所有範例使用 [`uv`](https://docs.astral.sh/uv/) 管理 Python 環境，DB 驅動採用 [`psycopg`](https://www.psycopg.org/) v3。

## 涵蓋主題

連線、CRUD、JOIN、Transaction、Connection Pool — 範例與詳細說明見 [`pgsql/README.md`](pgsql/README.md)。

## 環境需求

- Python 3.12+ 與 [uv](https://docs.astral.sh/uv/)
- 本機 PostgreSQL 16+（建議 17）
- macOS / Linux / Windows 皆可（範例以 macOS Homebrew + uv 撰寫）

## 快速開始

```bash
# 1. 安裝相依套件
uv sync

# 2. 建立 PostgreSQL 帳號與資料庫並匯入 schema
#    詳細步驟見 pgsql/README.md「建立帳號與資料庫」章節

# 3. 設定連線資訊
cp .env.example .env
# 編輯 .env 填入 PGUSER / PGPASSWORD / PGDATABASE

# 4. 跑第一個範例（驗證連線）
uv run python -m pgsql.try_00_connect
```

## 學習順序

`pgsql/` 內的範例檔名數字代表建議學習順序，由基本到進階：

| #  | 主題                | 檔案                       |
| -- | ------------------- | -------------------------- |
| 00 | 連線測試            | `try_00_connect.py`        |
| 01 | SELECT              | `try_01_select.py`         |
| 02 | INSERT（含 Faker）  | `try_02_insert.py`         |
| 03 | UPDATE（含 trigger）| `try_03_update.py`         |
| 04 | DELETE              | `try_04_delete.py`         |
| 05 | JOIN                | `try_05_join.py`           |
| 06 | Transaction         | `try_06_transaction.py`    |
| 07 | Connection Pool     | `try_07_pool.py`           |

每支腳本都附詳細中文註解，假設讀者只有基本 Python 知識。

## 安全注意事項

- 範例使用的預設密碼（如 `pgUser567`）**僅供本機練習**；切勿沿用於可被外網存取的 DB。
- `.env` 已被 `.gitignore` 排除，請確認你的真實密碼不會誤 commit。
- seed data（`data/shin02-pgsql.sql`）中的姓名 / email / 手機皆為生成的假資料。

## 授權

MIT License — 詳見 [LICENSE](LICENSE)
