# mongodb 模組

把 `data/shin03-mongo/` 底下的 NDJSON 檔匯入 MongoDB 的 `shin03` 資料庫。
**Collection 名稱直接取檔名**（去掉 `.ndjson` 副檔名）。

NDJSON 檔由 `mongodb/export_to_ndjson.py` 從 PostgreSQL 端產出，
詳見該檔 docstring。

## 前置

- 本機 MongoDB 已啟動（預設 `localhost:27017`）
- 安裝 `mongoimport`（隨 MongoDB Database Tools 安裝）

```bash
# macOS Homebrew
brew install mongodb-database-tools
```

## 匯入（批次）

從專案根目錄執行。`--drop` 會在匯入前清空 collection，確保可重複執行不會留下舊資料。

**macOS / Linux（bash / zsh）**

```bash
for col in members address_book categories products orders; do
  mongoimport --db=shin03 --collection="$col" --drop \
              --file="data/shin03-mongo/${col}.ndjson"
done
```

**Windows PowerShell**

換行續行字元是反引號 `` ` ``（不是 bash 的 `\`）；字串內的 `$col` 會自動展開。

```powershell
foreach ($col in 'members','address_book','categories','products','orders') {
    mongoimport --db=shin03 --collection=$col --drop `
                --file="data/shin03-mongo/$col.ndjson"
}
```

**Windows cmd**

cmd 的 `for` 沒有優雅的換行續行，整條寫一行；變數用 `%c`（寫進 `.bat` 檔要改成 `%%c`）。

```cmd
for %c in (members address_book categories products orders) do mongoimport --db=shin03 --collection=%c --drop --file=data\shin03-mongo\%c.ndjson
```

## 匯入（單檔）

**macOS / Linux**

```bash
mongoimport --db=shin03 --collection=address_book --drop \
            --file=data/shin03-mongo/address_book.ndjson
```

**Windows PowerShell**

```powershell
mongoimport --db=shin03 --collection=address_book --drop `
            --file="data/shin03-mongo/address_book.ndjson"
```

**Windows cmd**

```cmd
mongoimport --db=shin03 --collection=address_book --drop --file=data\shin03-mongo\address_book.ndjson
```

## 檔案與 collection 對應

| 檔案                  | Collection     | 文件數 |
| --------------------- | -------------- | ------ |
| `members.ndjson`      | `members`      | 3      |
| `address_book.ndjson` | `address_book` | 20     |
| `categories.ndjson`   | `categories`   | 9      |
| `products.ndjson`     | `products`     | 23     |
| `orders.ndjson`       | `orders`       | 3      |

> `orders` 的每筆文件內含 `details` 陣列（原 PostgreSQL 的 `order_details`
> 已嵌入為 embedded document），不需要也沒有獨立的 `order_details` collection。

## 關於日期欄位

NDJSON 內的日期 / 時間欄位用 [MongoDB Extended JSON](https://www.mongodb.com/docs/manual/reference/mongodb-extended-json/)
表達：

```json
"created_at": {"$date": "2024-07-08T09:52:01.000Z"}
```

`mongoimport` 會自動把它轉成 BSON `Date` 而不是字串，後續可以用
`$gte` / `$lte` 做日期區間查詢。

## 範例程式

`mongodb/` 內的 `try_NN_*.py` 範例檔名數字代表「建議學習順序」，由基本到進階。
每支腳本都對應一支 `pgsql/try_NN_*.py`，docstring 內標出兩個 DB 的關鍵差異。
執行任何範例前，請先用上面步驟把 NDJSON 匯入 MongoDB。

### `try_00_connect.py` — 連線健康檢查

連線、印出 MongoDB 版本與 `shin03` 內現有的 collection 清單。

```bash
uv run python -m mongodb.try_00_connect
```

### `try_01_select.py` — find 查詢

`address_book.find({}).sort("ab_id", -1).limit(5)` 取最後 5 筆。
特色：查詢條件是 dict 不是 SQL 字串；driver 直接回傳 dict（不用 `dict_row`）。

```bash
uv run python -m mongodb.try_01_select
```

### `try_02_insert.py` — insert_many 批次新增

用 Faker 產生 N 筆假資料寫入 `address_book`。
特色：直接塞 dict、schemaless（無需 ALTER TABLE）；`_id` 自動生成 `ObjectId`。

```bash
uv run python -m mongodb.try_02_insert         # 預設 5 筆
uv run python -m mongodb.try_02_insert 50      # 指定筆數（上限 100）
```

### `try_03_update.py` — update operators 與 $currentDate

依 `ab_id` 修改 `name`，用 `$currentDate` 在 server 端寫入 `updated_at`，
取代 PostgreSQL 的 BEFORE UPDATE trigger。

特色：update operators (`$set` / `$currentDate` / `$inc` / `$push` ...) 只改指定欄位；
`find_one_and_update + ReturnDocument.AFTER` 對應 SQL 的 `UPDATE ... RETURNING`。

> ⚠️ **`$currentDate` 是 update operator，不能用在 insert**
>
> 它只在 update 語境生效（`update_one` / `update_many` / `find_one_and_update`
> / `bulk_write` 的 update ops）。`insert_one` / `insert_many` 收的是字面文件，
> 直接把 `$currentDate` 塞進去會變成一個叫 `"$currentDate"` 的欄位，
> server 不會把它當運算子解讀。
>
> 想在 insert 時用 server-side 時間，有兩條路：
>
> 1. `update_one(filter, {"$setOnInsert": {...}, "$currentDate": {...}}, upsert=True)`
>    ── 但每筆都要一次 round trip，沒有 `insert_many` 的批次優勢。
> 2. client 端用 `datetime.now(timezone.utc)` 自己產生 tz-aware UTC
>    ── 簡單、能配 `insert_many`，是 `try_02_insert.py` 採用的作法。

```bash
uv run python -m mongodb.try_03_update 1 王小明
```

### `try_04_delete.py` — find_one_and_delete

依 `ab_id` 刪除一筆並印出被刪文件的全部欄位。
特色：原子完成「找 → 刪 → 回傳」，對應 SQL 的 `DELETE ... RETURNING *`。

```bash
uv run python -m mongodb.try_04_delete 1
```

### `try_05_join.py` — embedded vs $lookup（核心對比）

三段示範：

1. **embedded array**：直接讀 `orders.details` 子陣列，根本不用 JOIN
2. **$lookup**：跨集合關聯，預設行為相當於 LEFT JOIN（會員無訂單也會出現）
3. **多 stage pipeline**：4 表 JOIN 對應 `$lookup` × 2 + `$unwind` × 2 + `$project`

```bash
uv run python -m mongodb.try_05_join
```

### `try_06_transaction.py` — multi-document transaction

⚠️ 需要 **replica set**，standalone mongod 跑會在第一個 update 抛 `OperationFailure`
（腳本會抓住並優雅退出）。

特色：`client.start_session()` + `session.start_transaction()`，
所有要參與交易的操作都得帶 `session=session`。註解內解釋為何 MongoDB
因為 embedded document 設計常常根本不需要 transaction。

```bash
uv run python -m mongodb.try_06_transaction
```

啟動單節點 replica set 的快速指引：

```bash
mongod --dbpath /your/data/dir --replSet rs0
mongosh --eval 'rs.initiate()'
```

### `try_07_pool.py` — 連線池

8 個 thread 共用一個 `MongoClient(maxPoolSize=5)`，從 server 端 `serverStatus.connections`
觀察池的實際使用情況。

特色：🌟 **MongoClient 本身就是連線池**，不需要 wrapper（pgsql 範例用 psycopg-pool 包了一層）。
應用層不直接持有連線，每筆操作執行時短暫借 socket、結束立刻歸還。

```bash
uv run python -m mongodb.try_07_pool
```

## 驗證

```bash
mongosh shin03 --eval 'db.getCollectionNames()'
mongosh shin03 --eval 'db.address_book.countDocuments()'   # 應為 20
mongosh shin03 --eval 'db.orders.findOne()'                # 看 details 陣列
```

或進入 `mongosh shin03` 互動：

```javascript
use shin03
db.products.find({ category_id: 1 }).limit(3)
db.address_book.find({ birthday: { $gte: ISODate("1995-01-01") } })
```
