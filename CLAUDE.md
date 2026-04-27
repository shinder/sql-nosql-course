# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概覽

PostgreSQL（未來預計加入 NoSQL）連線練習專案。使用 `uv` 管理 Python 環境與相依套件，資料庫驅動採用 `psycopg` v3 與 `psycopg-pool`。

## 常用指令

所有指令從專案根目錄執行：

```bash
# 安裝 / 同步相依套件（以 uv.lock 為準）
uv sync

# 執行範例程式（一律以模組方式執行，因為 pgsql/ 內檔案會 import pgsql.config 等）
# 檔名數字代表建議學習順序：00 連線 → 01 SELECT → 02 INSERT → ... → 07 連線池
uv run python -m pgsql.try_00_connect      # 單次連線測試
uv run python -m pgsql.try_01_select       # SELECT 查詢
uv run python -m pgsql.try_07_pool         # 連線池併發測試
# 完整清單見 pgsql/README.md

# 型別檢查（pyproject.toml 已設定 [tool.ty.environment]）
uv run ty check
```

執行任何範例前，需先複製 `.env.example` 為 `.env` 並填入 `PGDATABASE` / `PGUSER` / `PGPASSWORD`。資料庫初始 schema 由 `data/shin02-pgsql.sql` 匯入（用 `psql` 執行，內含 `\gexec` metacommand）。

## 架構重點

### 連線設定的單一來源

`pgsql/config.py` 的 `get_conninfo()` 是**所有**連線參數的唯一進入點，從專案根目錄的 `.env` 讀取後組成 conninfo 字串。新增任何需要連線的程式時，請呼叫此函式而非自行讀環境變數，避免設定散落多處。

### psycopg 的 with-block 事務語意

所有範例的事務邊界都建立在 psycopg 的預設行為上，理解這一點才能正確讀懂程式：

- psycopg 預設 `autocommit=False`。
- `with psycopg.connect(...) as conn:` 區塊**正常結束會 commit**，**拋例外會 rollback**。
- `try_06_transaction.py` 是這個語意的示範；其他 CRUD demo（`try_02` ~ `try_04`）也都依賴這個機制隱式 commit。

要明確控制事務時，改用 `try / except / finally` 自己呼叫 `conn.commit()` / `conn.rollback()`，不要混用 with-block 與手動 commit。

### 連線池為 process 級單例

`pgsql/pool.py` 維護模組級的 `_pool` 變數。重點特性：

- `get_pool(min_size, max_size, timeout)` 的參數**僅在第一次呼叫時生效**；後續呼叫直接回傳既有池，傳入的參數會被忽略。
- 池建立後會 `pool.wait()` 等到 `min_size` 條連線都備妥才返回。
- 程式結束前須呼叫 `close_pool()`，否則會留下未關閉的背景連線。

需要使用連線池的新程式統一透過 `from pgsql.pool import get_pool, close_pool`。

### 資料庫角色設計

`pgsql/README.md` 描述的群組角色模式為本專案約定：

- `shin02_owners`（`NOLOGIN`）作為資料庫 OWNER，承擔擁有權但不能登入。
- `pguser` 為實際登入帳號，透過 `GRANT shin02_owners TO pguser` 繼承 OWNER 權限。
- 新增成員只需 `GRANT` 群組即可，不必逐一改授權。

修改資料庫權限相關內容時，請維持此設計，避免直接把 OWNER 改成個別使用者。

## 慣例

- 文件、註解、commit message 一律使用正體中文（沿用全域偏好）。
- `pgsql/` 內所有可執行檔以 `python -m pgsql.<name>` 方式啟動，import 路徑要寫成 `from pgsql.config import ...`，而不是相對 import。
- 教學用 demo 檔名格式為 `try_NN_<topic>.py`（如 `try_02_insert.py`）。`NN` 是教學順序編號，新增 demo 時延續這個慣例。函式庫檔（`config.py` / `pool.py` / `__init__.py`）不加數字前綴，因為會被其他檔 import。
- `data/shin02-pgsql.sql` 是從 MariaDB / phpMyAdmin dump 轉換而來，檔頭註解列出了所有改寫規則，未來若再從 MySQL/MariaDB 匯入新資料表時請依相同規則轉換。原始的 MariaDB dump 保留在 `data/shin02-mysql.sql` 供對照。
- `pyproject.toml` 用的是 `psycopg[binary]` 而不是純 `psycopg`，這是刻意的：binary extra 會帶入預編譯的 libpq，避免 Windows 上找不到系統 libpq 的問題。改 dependency 時別把 `[binary]` 拿掉。
