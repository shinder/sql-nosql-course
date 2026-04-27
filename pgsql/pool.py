"""PostgreSQL 連線池模組。

封裝 psycopg_pool.ConnectionPool 為 process 級單例，供其他模組共用。

使用方式：
    from pgsql.pool import get_pool

    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")

    # 程式結束前
    close_pool()

連線參數沿用 pgsql.connect.get_conninfo()，從 .env 讀取。
"""

# psycopg_pool 是 psycopg 官方提供的連線池套件（要另外安裝）。
# 「連線池」的概念：建立資料庫連線很慢（要 TCP 三次握手 + 認證），
# 所以先預先建立好幾條連線放在池子裡，需要時借出、用完歸還，
# 就不用每次查詢都重新建立連線。
from psycopg_pool import ConnectionPool

from pgsql.config import get_conninfo

# 模組層級變數，前面加底線 `_` 是 Python 慣例，表示「內部使用、不要從外部直接存取」。
# 型別標註 `ConnectionPool | None` 表示這個變數可能是 ConnectionPool 物件，也可能是 None。
# 一開始程式還沒建立池，所以是 None。
_pool: ConnectionPool | None = None


def get_pool(
    min_size: int = 2,
    max_size: int = 10,
    timeout: float = 10.0,
) -> ConnectionPool:
    """取得（或惰性建立）全域連線池。

    參數僅在第一次呼叫建立時生效；之後呼叫直接回傳既有的池。
    """
    # global 關鍵字：告訴 Python「我要修改外面那個 _pool 變數」，
    # 不寫的話，函式內的 _pool = ... 會被當成新建一個區域變數。
    global _pool

    # 「單例 (singleton)」模式：第一次呼叫才真的建立連線池，
    # 之後再呼叫 get_pool() 都直接回傳同一個池。
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=get_conninfo(),
            min_size=min_size,    # 池子最少保持幾條連線（即使閒置也不關掉）
            max_size=max_size,    # 池子最多開到幾條連線（同時最多併發查詢數）
            timeout=timeout,      # 借不到連線時最多等幾秒，超過就拋例外
            open=True,            # 建立物件時就立刻開池子（不要等第一次借連線才開）
        )
        # wait() 會卡住直到 min_size 條連線都建立完成，
        # 這樣可以確保「池建好之後就立刻可用」，避免第一次借連線時還在等。
        _pool.wait()
    return _pool


def close_pool() -> None:
    """關閉全域連線池（程式結束前呼叫）。"""
    global _pool
    if _pool is not None:
        # close() 會把池內所有連線都關掉，並拒絕之後的借用請求。
        # 沒呼叫的話，程式結束時會留下未關閉的背景連線，PostgreSQL 端會看到 idle 連線。
        _pool.close()
        _pool = None
