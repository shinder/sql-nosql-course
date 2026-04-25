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

-- 3. 建立資料庫，OWNER 指定為群組
CREATE DATABASE shin02 OWNER shin02_owners;

-- 4. 把 pguser 加入群組（之後要新增成員，重複此步驟即可）
GRANT shin02_owners TO pguser;
```

> - PostgreSQL 16+ 預設 role 為 `INHERIT`，加入群組後會自動取得權限；若 role 為 `NOINHERIT`，需先 `SET ROLE shin02_owners` 才生效。
> - 群組成員建立的 table/schema，擁有者預設是建立者本人。若希望物件也由群組共有，建立前先 `SET ROLE shin02_owners`，或事後 `ALTER TABLE ... OWNER TO shin02_owners`。

## 驗證連線

```bash
psql -h localhost -U pguser -d shin02
```

或透過本專案範例：

```bash
# 先複製 .env.example 為 .env，填入：
# PGUSER=pguser
# PGPASSWORD=pgUser567
# PGDATABASE=shin02
uv run python -m pgsql.connect
```

## 移除（如需重來）

```sql
DROP DATABASE IF EXISTS shin02;
DROP USER IF EXISTS pguser;
DROP ROLE IF EXISTS shin02_owners;
```
