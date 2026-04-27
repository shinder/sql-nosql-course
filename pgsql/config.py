"""連線設定來源。

從專案根目錄的 .env 讀取 PostgreSQL 連線參數，組成 conninfo 字串。
"""

# os 是 Python 內建模組，這裡只用它的 getenv() 來讀取「環境變數」
import os

# python-dotenv 是第三方套件，可以把 .env 檔的內容載入到環境變數裡，
# 這樣就能用 os.getenv() 取得，跟系統原生的環境變數沒有差別。
from dotenv import load_dotenv

# 一執行就讀取專案根目錄的 .env，把裡面的 KEY=VALUE 注入到環境變數。
# 為什麼要寫在這裡而不是函式裡面？因為這是「模組層級」的程式碼，
# 第一次 import pgsql.config 時就會執行一次，之後再 import 不會重跑。
load_dotenv()


def get_conninfo() -> str:
    # os.getenv("KEY", "default") — 如果環境變數 KEY 不存在，回傳第二個參數當預設值。
    # 這樣即使 .env 沒設，程式還是有合理的 fallback，不會直接爆掉。
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "postgres")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")

    # PostgreSQL 的「conninfo 字串」格式：用空白隔開的 key=value，
    # 例如 "host=localhost port=5432 dbname=shin02 user=pguser password=xxx"。
    # f"..." 是 Python 的 f-string，可以把 {變數} 直接代入字串裡。
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"
