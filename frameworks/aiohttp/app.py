import os
import aiohttp
import asyncio
import json

import asyncpg
# from sqlalchemy import create_engine, schema, Column
# from sqlalchemy.sql.expression import func
# from sqlalchemy.types import Integer, String
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

HOST = os.environ.get('DHOST', '127.0.0.1')
# engine = create_engine('postgres://benchmark:benchmark@%s:5432/benchmark' % HOST, pool_size=10)
# metadata = schema.MetaData()
# Base = declarative_base(metadata=metadata)
# Session = sessionmaker(bind=engine)
# class Message(Base):
#     __tablename__ = 'message'

#     id = Column(Integer, primary_key=True)
#     content = Column(String(length=512))


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


# async def db_payload():
#     session = Session()
#     messages = list(session.query(Message).order_by(func.random()).limit(100))
#     messages.append(Message(content='Hello, World!'))
#     messages.sort(key=lambda m: m.content)
#     return messages

# pool = None
# async def get_pool():
#     global pool
#     if pool is None:
#         pool = await asyncpg.create_pool(max_size=100,
#             user='benchmark', password='benchmark', database='benchmark', host=HOST,
#             timeout=60,
#             loop=asyncio.get_event_loop()
#         )
#     return pool

# async def db_payload():
    # pool = await get_pool()
    # conn = await pool.acquire()
    # messages = await conn.fetch('''SELECT * FROM message LIMIT 100;''')
    # data = {'data': {m.get('id'): m.get('content') for m in messages}}
    # pool.release(conn)
    # return data

async def complete(request):
    # messages = await db_payload()
    # return aiohttp.web.Response(
    #     text=json.dumps({'data': {m.id: m.content for m in messages}}),
    #     content_type='application/json'
    # )
    pool = request.app['pool']
    async with pool.acquire() as conn:
        messages = await conn.fetch('''SELECT * FROM message LIMIT 100;''')
        data = {'data': {m.get('id'): m.get('content') for m in messages}}
        return aiohttp.web.Response(
            text=json.dumps(data),
            content_type='application/json'
        )

# app = aiohttp.web.Application()


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


# aiohttp.web.run_app(app)