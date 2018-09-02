import asyncio
import cProfile
import contextlib
import pstats
import time
from io import StringIO

import asyncpg
import psycopg2
import uvloop
from asyncpg import create_pool


@contextlib.contextmanager
def profiled(dbapi):
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    pr.dump_stats("profile.stats")
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print("DBAPI:  %s" % dbapi.__name__)
    print(s.getvalue())


@contextlib.contextmanager
def timeonly(dbapi):
    now = time.time()
    try:
        yield
    finally:
        total = time.time() - now
        print("DBAPI:  %s, total seconds %f" % (dbapi.__name__, total))


def go(dbapi, ctx):
    '''
    同步性能测试
    :param dbapi: 数据库连接引擎
    :param ctx: 性能评估的上下文管理器
    :return:
    '''
    conn = dbapi.connect(
        user='postgres',
        password='root',
        host='127.0.0.1',
        dbname='test')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_things (
        x INTEGER,
        y VARCHAR(255),
        z FLOAT
    )
    """)

    cursor.execute("DELETE from test_things")
    cursor.close()
    conn.commit()

    cursor = conn.cursor()

    with ctx(dbapi):
        for row in range(1000):
            cursor.execute(
                "INSERT INTO test_things (x, y, z) "
                "VALUES (%(x)s, %(y)s, %(z)s)",
                {"x": row, "y": "row number %d" % row,
                 "z": row * 4.57292, }
            )

        for x in range(500):
            cursor.execute(
                "select * from test_things")
            rows = cursor.fetchall()
            for row in rows:
                row[0], row[1], row[2]
    cursor.close()
    conn.close()


async def insert_data(pool, row):
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO test_things (x, y, z) "
            "VALUES ($1, $2, $3)", row, "row number %d" % row, row * 4.57292
        )


async def select_data(pool):
    async with pool.acquire() as connection:
        rows = await connection.fetch("select * from test_things")
        for _ in rows:
            _


async def main(dbapi, ctx):
    '''
    异步性能测试（原生事件循环以及uvloop）
    :param dbapi: 事件协议
    :param ctx: 性能评估的上下文管理器
    :return:
    '''
    # Establish a connection to an existing database named "test"
    pool = await create_pool(
        user='postgres', password='root', host='127.0.0.1', database='test')
    # Execute a statement to create a new table.
    async with pool.acquire() as connection:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS test_things (
                x INTEGER,
                y VARCHAR(255),
                z FLOAT
            )
            """)
        await connection.execute("DELETE from test_things")
    with ctx(dbapi):
        to_do = [insert_data(pool, row) for row in range(1000)]
        await asyncio.wait(to_do)
        to_do = [select_data(pool) for _ in range(500)]
        await asyncio.wait(to_do)  # <10>

if __name__ == '__main__':
    # go(psycopg2, profiled)  # sync
    #
    # asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(asyncpg,profiled))  # async default loop
    #
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(uvloop, profiled))  # async uvloop
    #
    go(psycopg2, timeonly)
    #
    # asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(asyncpg, timeonly))
    #
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(uvloop, timeonly))
