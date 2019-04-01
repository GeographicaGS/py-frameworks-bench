import os
import aiohttp
import asyncio
import json

from sqlalchemy import create_engine, schema, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

HOST = os.environ.get('DHOST', '127.0.0.1')
engine = create_engine('postgres://benchmark:benchmark@%s:5432/benchmark' % HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)
class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))


async def json(request):
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


async def db_payload():
    session = Session()
    messages = list(session.query(Message).order_by(func.random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    return messages

async def complete(request):
    messages = await db_payload()
    return aiohttp.web.Response(
        text=json.dumps({'data': {m.id: m.content for m in messages}}),
        content_type='application/json'
    )

app = aiohttp.web.Application()
app.router.add_route('GET', '/json', json)
app.router.add_route('GET', '/remote', remote)
app.router.add_route('GET', '/complete', complete)
