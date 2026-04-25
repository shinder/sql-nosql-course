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

from psycopg_pool import ConnectionPool

from pgsql.config import get_conninfo

_pool: ConnectionPool | None = None


def get_pool(
    min_size: int = 2,
    max_size: int = 10,
    timeout: float = 10.0,
) -> ConnectionPool:
    """取得（或惰性建立）全域連線池。

    參數僅在第一次呼叫建立時生效；之後呼叫直接回傳既有的池。
    """
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=get_conninfo(),
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            open=True,
        )
        _pool.wait()
    return _pool


def close_pool() -> None:
    """關閉全域連線池（程式結束前呼叫）。"""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
