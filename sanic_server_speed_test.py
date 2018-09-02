import asyncpg
from sanic import Sanic
from sanic.response import json
from asyncpg import connect, create_pool

def creat_app():
    app = Sanic(__name__)

    @app.listener('before_server_start')
    async def setup_db(app, loop):
        app.pool = await create_pool(
            user='postgres', password='root', host='127.0.0.1', database='test', loop=loop, max_size=100)
        async with app.pool.acquire() as connection:
            # Execute a statement to create a new table.
            await connection.execute("""
                    CREATE TABLE IF NOT EXISTS test_things (
                        x INTEGER,
                        y VARCHAR(255),
                        z FLOAT
                    )
                    """)

            await connection.execute("DELETE from test_things")
            row = 1
            await connection.execute(
                "INSERT INTO test_things (x, y, z) "
                "VALUES ($1, $2, $3)", row, "row number %d" % row, row * 4.57292
            )

    @app.route('/db')
    async def test_db(request):
        async with app.pool.acquire() as connection:
            rows = await connection.fetch("select * from test_things")
            return json(rows)
    return app


app = creat_app()
if __name__ == '__main__':
    app.run(port=8080, debug=False)
