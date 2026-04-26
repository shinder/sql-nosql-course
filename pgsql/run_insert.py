"""產生隨機資料並批次寫入 public.address_book。

執行方式（從專案根目錄）：
    uv run python -m pgsql.run_insert         # 預設新增 5 筆
    uv run python -m pgsql.run_insert 50      # 指定筆數（上限 100）
"""

import random
import sys
from datetime import datetime

import psycopg
from faker import Faker

from pgsql.config import get_conninfo

fake = Faker("zh_TW")

DEFAULT_ROWS = 5
MAX_ROWS = 100

CITIES = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "嘉義市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣",
    "澎湖縣", "金門縣", "連江縣",
]


def make_row() -> tuple:
    name = fake.name()
    email = fake.email()
    mobile = "09" + "".join(random.choices("0123456789", k=8))
    birthday = fake.date_of_birth(minimum_age=20, maximum_age=60)
    address = random.choice(CITIES)
    created_at = datetime.now()
    return (name, email, mobile, birthday, address, created_at)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROWS
    if n > MAX_ROWS:
        sys.exit(f"筆數最多 {MAX_ROWS}（指定為 {n}）")
    if n < 1:
        sys.exit(f"筆數需大於 0（指定為 {n}）")
    rows = [make_row() for _ in range(n)]

    sql = """
        INSERT INTO public.address_book
            (name, email, mobile, birthday, address, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ab_id
    """

    with psycopg.connect(get_conninfo()) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows, returning=True)
            inserted_ids = []
            while True:
                inserted_ids.append(cur.fetchone()[0])
                if not cur.nextset():
                    break

    print(f"已新增 {len(inserted_ids)} 筆資料，ab_id 範圍：{inserted_ids[0]} ~ {inserted_ids[-1]}")
    print("\n前 3 筆樣本：")
    for row in rows[:3]:
        print(f"  {row}")


if __name__ == "__main__":
    main()
