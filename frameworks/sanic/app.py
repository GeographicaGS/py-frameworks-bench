import os
import aiohttp
import psycopg2
from sanic import Sanic, Blueprint
from sanic.response import text, json, html
import asyncpg


HOST = os.environ.get('DHOST', '127.0.0.1')


bp = Blueprint('dp')

class pg:
    def __init__(self, pg_pool):
        self.pg_pool = pg_pool

    async def fetch(self, sql, *args, **kwargs):
        async with self.pg_pool.acquire() as connection:
            return await connection.fetch(sql, *args, **kwargs)

    async def execute(self, sql, *args, **kwargs):
        async with self.pg_pool.acquire() as connection:
            return await connection.execute(sql, *args, **kwargs)

@bp.listener('before_server_start')
async def init_pg(app, loop):
    """
    Init Postgresql DB.
    """
    bp.pg_pool = await asyncpg.create_pool(
        user='benchmark', password='benchmark', database='benchmark', host=HOST,
        max_inactive_connection_lifetime=60,
        min_size=1,
        max_size=20,
        loop=loop
    )
    app.pg = pg(bp.pg_pool)
    print(' -- Setup connection pool -- ')

app = Sanic()
app.blueprint(bp)


# JSON
@app.route("/json")
async def json_endpoint(request):
    return json({'message': 'Hello, World!'})


# Remote
async def get_url(session, url):
    async with session.get(url) as response:
        return await response.text()

@app.route("/remote")
async def remote(request):
    async with aiohttp.ClientSession() as session:
        response_text = await get_url(session, 'http://%s' % HOST)
        return html(response_text)


# Complete
@app.route("/complete")
async def complete(request):
    messages = await app.pg.fetch('SELECT * FROM message LIMIT 100;')
    data = {'data': {m.get('id'): m.get('content') for m in messages}}
    return json(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)