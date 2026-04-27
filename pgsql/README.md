# pgsql 模組

PostgreSQL 連線範例與設定筆記。

## 建立帳號與資料庫

採用「群組角色」作為資料庫 OWNER 的設計：群組本身不登入，只承擔擁有權；
實際使用的帳號（如 `pguser`）加入群組後即繼承 OWNER 等級權限。
未來要再加入新成員，只需 `GRANT` 群組即可，不必逐一改授權。

以 superuser（macOS Homebrew 安裝預設為當前使用者）連入：

```bash
psql postgres
```

執行下列 SQL：

```sql
-- 1. 建立群組角色（NOLOGIN：不能直接登入，只用來持有權限）
CREATE ROLE shin02_owners NOLOGIN;

-- 2. 建立登入用帳號 pguser，密碼 pgUser567
CREATE USER pguser WITH PASSWORD 'pgUser567';

-- 3. OWNER 指定為群組
CREATE DATABASE shin02 OWNER shin02_owners;

-- 4. 把 pguser 加入群組（之後要新增成員，重複此步驟即可）
GRANT shin02_owners TO pguser;

-- 5. 使用 pguser 登入，匯入 SQL 建立資料表
psql -h localhost -U pguser -d shin02
\i data/shin02-pgsql.sql
```

> - PostgreSQL 16+ 預設 role 為 `INHERIT`，加入群組後會自動取得權限；若 role 為 `NOINHERIT`，需先 `SET ROLE shin02_owners` 才生效。
> - 群組成員建立的 table/schema，擁有者預設是建立者本人。若希望物件也由群組共有，建立前先 `SET ROLE shin02_owners`，或事後 `ALTER TABLE ... OWNER TO shin02_owners`。

## 驗證連線

用 `psql` 直接驗證：

```bash
psql -h localhost -U pguser -d shin02
```

或先複製 `.env.example` 為 `.env`，填入下列三項，再用本專案範例：

```
PGUSER=pguser
PGPASSWORD=pgUser567
PGDATABASE=shin02
```

## 範例程式

所有指令從專案根目錄執行。

### `try_connect.py` — 單次連線測試

建立一條連線、查詢 `SELECT version()`、關閉。用來確認 `.env` 與帳號權限設定無誤。

```bash
uv run python -m pgsql.try_connect
```

預期輸出：

```
PostgreSQL 版本： PostgreSQL 16.x ...
```

### `try_pool.py` — 連線池測試

驗證 `pgsql.pool.get_pool()` 單例：

1. 從池借出單一連線，印出 `current_database` / `current_user`
2. 開 8 個 thread 搶 5 條連線上限（每個查詢 sleep 0.5s），觀察排隊行為
3. 印出 `pool.get_stats()` 統計

```bash
uv run python -m pgsql.try_pool
```

預期約 1.0s 完成（兩批排隊：5 + 3）。可調整 `main()` 內的 `min_size` / `max_size` 觀察差異。

### `run_select.py` — SELECT 查詢範例

讀取 `public.address_book` 表，依 `ab_id` 由大到小取前 5 筆並印出每個欄位。
使用 `psycopg.rows.dict_row` 讓 `fetchall()` 直接回傳 dict。

```bash
uv run python -m pgsql.run_select
```

### `run_insert.py` — INSERT 批次新增範例

用 `Faker('zh_TW')` 產生隨機資料，透過 `cursor.executemany(..., returning=True)`
批次寫入 `public.address_book`，並印出新增的 `ab_id` 範圍與前 3 筆樣本。

```bash
uv run python -m pgsql.run_insert         # 預設 5 筆
uv run python -m pgsql.run_insert 50      # 指定筆數（上限 100）
```

欄位產生方式：

- `name` / `email` / `birthday`：`fake.name()` / `fake.email()` / `fake.date_of_birth()`
- `mobile`：自製 `09` + 8 位亂數，貼近 seed 資料的 `0918xxxxxxx` 風格
- `address`：從 22 個直轄市 / 縣市清單隨機挑一個（與 seed 資料一致）
- `created_at`：`datetime.now()`

### `run_update.py` — UPDATE 範例

依命令列傳入的 `ab_id` 修改該筆資料的 `name` 欄位，
透過 `RETURNING ab_id, name, email` 印出更新後的結果（email 用來協助辨識是否改到對的人）。

```bash
uv run python -m pgsql.run_update 123 王小明     # 把 ab_id=123 的 name 改成「王小明」
```

兩個參數都必填，沒給會直接結束、印出用法。

### `run_delete.py` — DELETE 範例

依命令列傳入的 `ab_id` 刪除一筆資料，並用 `RETURNING *` 印出剛被刪掉的整列內容。
找不到符合的列時會明確提示並以 exit code 1 結束。

```bash
uv run python -m pgsql.run_delete 123     # 刪除 ab_id=123
```

刪除是破壞性操作，所以**不設預設值**：沒傳參數會直接結束、印出用法。

## 移除（如需重來）

```sql
DROP DATABASE IF EXISTS shin02;
DROP USER IF EXISTS pguser;
DROP ROLE IF EXISTS shin02_owners;
```
