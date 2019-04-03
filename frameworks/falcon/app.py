import os
import json
import falcon
import psycopg2
import requests

HOST = os.environ.get('DHOST', '127.0.0.1')

db_conn = psycopg2.connect(
    user = 'benchmark',
    password = 'benchmark',
    host = HOST,
    database = 'benchmark'
)

class JSONResource(object):
    def on_get(self, request, response):
        json_data = {'message': 'Hello, world!'}
        response.media = json_data

class RemoteResource(object):

    def on_get(self, request, response):
        remote_response = requests.get('http://%s' % HOST)
        response.set_header('Content-Type', 'text/html')
        response.body = remote_response.text


class CompleteResource(object):
    def on_get(self, request, response):
        with db_conn.cursor() as cursor:
            cursor.execute('''SELECT * FROM message LIMIT 100;''')
            messages = cursor.fetchall()
            data = {'data': {m[0]: m[1] for m in messages}}
            response.media = data


app = falcon.API()

app.add_route('/json', JSONResource())
app.add_route('/remote', RemoteResource())
app.add_route('/complete', CompleteResource())
