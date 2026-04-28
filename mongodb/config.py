"""MongoDB 連線設定來源。

從專案根目錄的 .env 讀取 MongoDB 連線資訊。所有連 MongoDB 的程式都應該透過
這裡取得 URI / database 名稱，避免設定散落多處。
"""

import os

from dotenv import load_dotenv

# 載入專案根目錄的 .env（與 pgsql/config.py 共用同一份檔）。
# 模組層級執行：第一次 import mongodb.config 時跑一次，後續 import 不會重跑。
load_dotenv()


def get_mongo_uri() -> str:
    """回傳 MongoDB 連線 URI。

    本機預設沒有認證，URI 形如 `mongodb://localhost:27017`。
    若日後改用 Atlas 或加上帳密，URI 會長得像：
      mongodb+srv://user:pwd@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
    所有變化都集中在 .env 內，程式不用改。
    """
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")


def get_db_name() -> str:
    """回傳要使用的 database 名稱（預設 `shin03`）。"""
    return os.getenv("MONGO_DATABASE", "shin03")
