import os
import sys
import json
import aiohttp

import signal
import logging

from tornado import web, gen, httpclient, httpserver, ioloop

from sqlalchemy import create_engine, schema, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

HOST = os.environ.get('DHOST', '127.0.0.1')
engine = create_engine('postgres://benchmark:benchmark@%s:5432/benchmark' % HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)
class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))



class JSONHandler(web.RequestHandler):

    async def payload(self):
        self.write({'message': 'Hello, World!'})

    async def get(self):
        # await self.payload()
        self.write({'message': 'Hello, World!'})
        self.finish()


class RemoteHandler(web.RequestHandler):

    async def get_url(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def get(self):
        async with aiohttp.ClientSession() as session:
            response_text = await self.get_url(session, 'http://%s' % HOST)
            self.write(response_text)
            self.finish()


class CompleteHandler(web.RequestHandler):

    async def db_payload(self):
        session = Session()
        messages = list(session.query(Message).order_by(func.random()).limit(100))
        messages.append(Message(content='Hello, World!'))
        messages.sort(key=lambda m: m.content)
        session.close()
        return {'data': {m.id: m.content for m in messages}}

    async def get(self):
        self.set_header("Content-Type", 'application/json')
        data = await self.db_payload()
        self.write(json.dumps(data))
        self.finish()


app = web.Application(
    [
        web.url('/json',    JSONHandler),
        web.url('/remote',  RemoteHandler),
        web.url('/complete', CompleteHandler),
    ]
)


if __name__ == '__main__':
    logging.info('Starting HTTP server.')

    with open('pid', 'w') as f:
        f.write(str(os.getpid()))

    try:
        server = httpserver.HTTPServer(app)
        server.bind(5000, "0.0.0.0")
        server.start(2)

        # loop = ioloop.IOLoop.instance()
        # loop.start()
        # app.listen(5000, "0.0.0.0")

        ioloop.IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        server.stop()
        loop = ioloop.IOLoop.instance()
        loop.stop()
        sys.exit(0)


# pylama:ignore=E402
