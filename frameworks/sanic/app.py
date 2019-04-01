import os
import aiohttp
import psycopg2
from sanic import Sanic
from sanic.response import text, json, html

from sqlalchemy import create_engine, schema, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Sanic()


HOST = os.environ.get('DHOST', '127.0.0.1')
engine = create_engine('postgres://benchmark:benchmark@%s:5432/benchmark' % HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)
class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))


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
async def db_payload():
    session = Session()
    messages = list(session.query(Message).order_by(func.random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    return messages

@app.route("/complete")
async def complete(request):
    messages = await db_payload()
    return json({'data': {m.id: m.content for m in messages}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)