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

### Windows 上 `\i` 的路徑寫法

psql 的 `\i` metacommand 在 Windows 上要特別注意兩件事，否則會踩到 `Permission denied` 或編碼錯誤：

1. **路徑用單引號 + 正斜線**

   ```
   \i 'C:/Users/shin/Documents/sql-nosql-course/data/shin02-pgsql.sql'
   ```

   - **單引號**：psql 的雙引號 (`"`) 是給 SQL identifier（table / column 名）用的，不是給檔名。
   - **正斜線 `/`**：反斜線 `\` 是 psql 的 escape 字元，路徑裡的 `\U` `\D` 之類會被誤解。寫成 `\i C:\Users\shin\...` 通常會出 `C:: Permission denied`。
     正斜線在 Windows libpq 完全合法。

2. **編碼問題**：Windows cmd 預設 codepage 是 CP950 (Big5)，psql 啟動後 `client_encoding` 也跟著變 BIG5，讀含中文的 UTF-8 SQL 檔會炸。本專案的 `data/shin02-pgsql.sql` 在 `BEGIN;` 之後就有一行 `SET client_encoding = 'UTF8';` 預先處理掉這個問題。寫自己的 SQL 檔時記得也加。

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

所有指令從專案根目錄執行。檔名數字代表「建議學習順序」，從基本到進階：

### `try_00_connect.py` — 單次連線測試

建立一條連線、查詢 `SELECT version()`、關閉。用來確認 `.env` 與帳號權限設定無誤。

```bash
uv run python -m pgsql.try_00_connect
```

預期輸出：

```
PostgreSQL 版本： PostgreSQL 16.x ...
```

### `try_01_select.py` — SELECT 查詢範例

讀取 `public.address_book` 表，依 `ab_id` 由大到小取前 5 筆並印出每個欄位。
使用 `psycopg.rows.dict_row` 讓 `fetchall()` 直接回傳 dict。

```bash
uv run python -m pgsql.try_01_select
```

### `try_02_insert.py` — INSERT 批次新增範例

用 `Faker('zh_TW')` 產生隨機資料，透過 `cursor.executemany(..., returning=True)`
批次寫入 `public.address_book`，並印出新增的 `ab_id` 範圍與前 3 筆樣本。

```bash
uv run python -m pgsql.try_02_insert         # 預設 5 筆
uv run python -m pgsql.try_02_insert 50      # 指定筆數（上限 100）
```

欄位產生方式：

- `name` / `email` / `birthday`：`fake.name()` / `fake.email()` / `fake.date_of_birth()`
- `mobile`：自製 `09` + 8 位亂數，貼近 seed 資料的 `0918xxxxxxx` 風格
- `address`：從 22 個直轄市 / 縣市清單隨機挑一個（與 seed 資料一致）
- `created_at`：`datetime.now()`

### `try_03_update.py` — UPDATE 範例

依命令列傳入的 `ab_id` 修改該筆資料的 `name` 欄位，
透過 `RETURNING ab_id, name, email` 印出更新後的結果（email 用來協助辨識是否改到對的人）。

```bash
uv run python -m pgsql.try_03_update 123 王小明     # 把 ab_id=123 的 name 改成「王小明」
```

兩個參數都必填，沒給會直接結束、印出用法。

### `try_04_delete.py` — DELETE 範例

依命令列傳入的 `ab_id` 刪除一筆資料，並用 `RETURNING *` 印出剛被刪掉的整列內容。
找不到符合的列時會明確提示並以 exit code 1 結束。

```bash
uv run python -m pgsql.try_04_delete 123     # 刪除 ab_id=123
```

刪除是破壞性操作，所以**不設預設值**：沒傳參數會直接結束、印出用法。

### `try_05_join.py` — JOIN 範例

用 `members` / `orders` / `order_details` / `products` 四張表示範三種 JOIN：

1. **INNER JOIN**（orders × members）：列出每筆訂單與下單會員
2. **LEFT JOIN**（members × orders + GROUP BY）：列出所有會員與其訂單數，沒下單的會員會以 `order_count=0` 出現
3. **多表 JOIN**（4 張表）：訂單明細查詢，含會員、書名、小計

```bash
uv run python -m pgsql.try_05_join
```

seed 資料的會員「瑪麗亞」沒下過任何訂單，正好用來凸顯 INNER 與 LEFT 的差別 ──
INNER 看不到她、LEFT 才看得到。

### `try_06_transaction.py` — 交易（atomicity）示範

挑出 `address_book` 最新兩筆做兩次 `UPDATE`，演示交易的原子性：

- **場景 A**：第一個 UPDATE 跑完後故意拋例外 → 離開 `with psycopg.connect(...)` 區塊時自動 rollback → 重新查詢時兩筆都「沒變」
- **場景 B**：兩個 UPDATE 都成功 → 區塊正常結束自動 commit → 兩筆都被改了
- 最後還原成原始資料，腳本可重複執行

```bash
uv run python -m pgsql.try_06_transaction
```

關鍵觀念：psycopg 預設 `autocommit=False`，`with psycopg.connect(...)` 區塊正常結束會 commit、
拋例外會 rollback；想明確控制就改用 `try / except / finally` 自己呼叫 `conn.commit()` / `conn.rollback()`。

### `try_07_pool.py` — 連線池測試

驗證 `pgsql.pool.get_pool()` 單例：

1. 從池借出單一連線，印出 `current_database` / `current_user`
2. 開 8 個 thread 搶 5 條連線上限（每個查詢 sleep 0.5s），觀察排隊行為
3. 印出 `pool.get_stats()` 統計

```bash
uv run python -m pgsql.try_07_pool
```

預期約 1.0s 完成（兩批排隊：5 + 3）。可調整 `main()` 內的 `min_size` / `max_size` 觀察差異。

## 移除（如需重來）

```sql
DROP DATABASE IF EXISTS shin02;
DROP USER IF EXISTS pguser;
DROP ROLE IF EXISTS shin02_owners;
```
