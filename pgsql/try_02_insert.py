"""產生隨機資料並批次寫入 public.address_book。

執行方式（從專案根目錄）：
    uv run python -m pgsql.try_02_insert         # 預設新增 5 筆
    uv run python -m pgsql.try_02_insert 50      # 指定筆數（上限 100）
"""

# random：Python 內建的亂數模組
# sys：用來讀取命令列參數 sys.argv
# datetime：產生「現在時間」當作 created_at 欄位的值
import random
import sys
from datetime import datetime

import psycopg

# Faker 是第三方套件，用來產生「假資料」（姓名、email、地址、生日等），
# 在開發階段常用來灌測試資料，免得自己手刻。
from faker import Faker

from pgsql.config import get_conninfo

# Faker("zh_TW") 指定使用「繁體中文（台灣）」的 locale，
# 這樣 fake.name() 會出中文姓名（如「林月娥」）而不是英文。
# 模組載入時就建一個共用的 fake 實例，不必每次呼叫 make_row() 都重建。
fake = Faker("zh_TW")

# 全大寫變數名是 Python 慣例，表示「常數」（程式不會去修改它）。
DEFAULT_ROWS = 5
MAX_ROWS = 100

# 22 個直轄市 / 縣市清單。
# 為什麼不用 fake.address()？因為 Faker 的 zh_TW 地址會拼出
# 「717 中和縣德街988號之3」這種怪字串，跟 seed 資料只放縣市的風格不一致。
CITIES = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "嘉義市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣",
    "澎湖縣", "金門縣", "連江縣",
]


def make_row() -> tuple:
    """產生一筆假資料，回傳 tuple 對應 INSERT 的欄位順序。"""
    name = fake.name()
    email = fake.email()

    # random.choices(序列, k=N) 從序列中「可重複地」抽 N 個，回傳 list。
    # 注意有 s 結尾：random.choice (沒 s) 抽一個元素、random.choices (有 s) 抽一個 list。
    # "".join([...]) 把 list 裡的字串一個個串起來，中間不放分隔符 → 變一整串數字。
    # 結果範例：'09' + '12345678' → '0912345678'
    mobile = "09" + "".join(random.choices("0123456789", k=8))

    # date_of_birth 會根據今天日期回推一個合理的生日（範圍可調）。
    birthday = fake.date_of_birth(minimum_age=20, maximum_age=60)

    address = random.choice(CITIES)

    # datetime.now() 取得「現在的本地時間」，沒有時區資訊（naive datetime），
    # 對應 PostgreSQL 的 TIMESTAMP（不含時區）型別。
    created_at = datetime.now()

    # 回傳 tuple，順序要跟下面 INSERT 的欄位順序一一對應。
    return (name, email, mobile, birthday, address, created_at)


def main() -> None:
    # sys.argv 是 list，第 0 個是檔案名稱，第 1 個之後才是使用者傳的參數。
    # `len(sys.argv) > 1` 確認真的有傳參數，避免 IndexError。
    # int(...) 把字串參數轉成整數，傳「abc」會炸 ValueError（這裡先不處理，保持簡單）。
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROWS

    # sys.exit(訊息) 直接結束程式，並印出訊息到 stderr，exit code 為 1。
    if n > MAX_ROWS:
        sys.exit(f"筆數最多 {MAX_ROWS}（指定為 {n}）")
    if n < 1:
        sys.exit(f"筆數需大於 0（指定為 {n}）")

    # List comprehension：等同於 for 迴圈一個個 append 到 list。
    # `_` 是 Python 慣例，表示「這個變數不會用到」（這裡只是要跑 n 次而已）。
    rows = [make_row() for _ in range(n)]

    # 三引號字串可以跨多行，方便寫長 SQL。
    # %s 是 psycopg 的「placeholder（佔位符）」，注意不是 Python 的字串格式化！
    # 實際的值由 executemany 的第二個參數帶入，psycopg 會幫你做跳脫，避免 SQL injection。
    # ⚠️ 千萬不要用 f-string 把使用者輸入直接拼進 SQL，那是 SQL injection 的經典寫法。
    # RETURNING ab_id：PostgreSQL 特有語法，INSERT 後直接回傳剛產生的欄位值（這裡是自動編號的 PK）。
    sql = """
        INSERT INTO public.address_book
            (name, email, mobile, birthday, address, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ab_id
    """

    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            # executemany(sql, [tuple, tuple, ...]) 對同一條 SQL 跑多次，
            # 每次代入 list 裡的一個 tuple，比 for 迴圈呼叫 execute() 快很多。
            # returning=True：psycopg 3 的選項，告訴它要保留每次 INSERT 的 RETURNING 結果。
            cur.executemany(sql, rows, returning=True)

            # executemany + RETURNING 的結果是「多個 result set」（每筆一個），
            # 要用 nextset() 切換到下一個。一般 SELECT 沒有這個問題（只有一個 result set）。
            inserted_ids = []
            while True:
                # fetchone() 取當前 result set 的第一列；這裡每個 result set 只有一列。
                # row[0] 是 RETURNING ab_id 回傳的那個值。
                inserted_ids.append(cur.fetchone()[0])
                # nextset() 切到下一個 result set，沒有的話回傳 None（while 結束）。
                if not cur.nextset():
                    break

    # 離開 with psycopg.connect(...) 區塊時，psycopg 會自動 commit（沒出例外的話），
    # 所以這裡不用顯式呼叫 conn.commit()。
    print(f"已新增 {len(inserted_ids)} 筆資料，ab_id 範圍：{inserted_ids[0]} ~ {inserted_ids[-1]}")
    print("\n前 3 筆樣本：")
    # rows[:3] 是「切片 (slice)」語法，取 list 的前 3 個元素（不會炸界，自動截斷）。
    for row in rows[:3]:
        print(f"  {row}")


if __name__ == "__main__":
    main()
