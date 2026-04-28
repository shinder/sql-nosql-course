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

從專案根目錄執行。`--drop` 會在匯入前清空 collection，確保可重複執行不會留下舊資料：

```bash
for col in members address_book categories products orders; do
  mongoimport --db=shin03 --collection="$col" --drop \
              --file="data/shin03-mongo/${col}.ndjson"
done
```

## 匯入（單檔）

```bash
mongoimport --db=shin03 --collection=address_book --drop \
            --file=data/shin03-mongo/address_book.ndjson
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
