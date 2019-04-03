import os
import aiohttp
import asyncio
import json

import asyncpg
import uvloop

HOST = os.environ.get('DHOST', '127.0.0.1')


async def json_ep(request):
    return aiohttp.web.Response(
        text=json.dumps({'message': 'Hello, World!'}),
        content_type='application/json'
    )


async def get_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def remote(request):
    async with aiohttp.ClientSession() as session:
        response_text = await get_url(session, 'http://%s' % HOST)
        return aiohttp.web.Response(text=response_text, content_type='text/html')


async def complete(request):
    pool = request.app['pool']
    async with pool.acquire() as conn:
        messages = await conn.fetch('''SELECT * FROM message LIMIT 100;''')
        data = {'data': {m.get('id'): m.get('content') for m in messages}}
        return aiohttp.web.Response(
            text=json.dumps(data),
            content_type='application/json'
        )


async def init_app():
    """Initialize the application server."""
    app = aiohttp.web.Application()
    # Create a database connection pool
    app['pool'] = await asyncpg.create_pool(
        user='benchmark', password='benchmark', database='benchmark', host=HOST,
        min_size=1, max_size=20
    )
    print(' -- Setup connection pool -- ')
    return app


loop = asyncio.get_event_loop()
app = loop.run_until_complete(init_app())

app.router.add_route('GET', '/json', json_ep)
app.router.add_route('GET', '/remote', remote)
app.router.add_route('GET', '/complete', complete)

