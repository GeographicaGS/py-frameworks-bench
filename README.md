Python frameworks' benchmarks
=============================

There are some benchmarks for popular python frameworks.

* [Aiohttp](https://github.com/KeepSafe/aiohttp)       -- Http client/server for asyncio
* [Django](https://github.com/django/django)           -- The Web framework for perfectionists with deadlines
* [Falcon](https://github.com/falconry/falcon)         -- A high-performance Python framework for building cloud APIs
* [Flask](https://github.com/mitsuhiko/flask)          -- A microframework based on Werkzeug, Jinja2 and good intentions
* [Tornado](https://github.com/tornadoweb/tornado)     -- A Python web framework and asynchronous networking library
* [Sanic](https://github.com/huge-success/sanic)

The goal of the project is not tests for deployment (like uwsgi vs gunicorn and
etc) but instead tests the frameworks itself.


## Setup and ussage:

```
# Note you'll have to delete the docker the next time... (TODO: Fix this)
make docker
make docker-run
make db # Fills DB

# and let's say:
 virtualenv -p python3 .venv
 . .venv/bin/activate
 pip install -r requirements.txt
 
 ...
 
 make bench
 
 # Results at results.csv
```

#### Some notes:
    ... You can (and should) edit Makefile to run only the required frameworks.
    Just uncomment the one(s) you want to test under the `bench` block.
    The resson: Some of them are not properly closed and results may not be true, eventually.
    i.e:
    	* Tornado keeps running after tests ending, that's why it's the last one)
    	* Sanic sometimes takes too much time before stop, so it's beter to be the last one too.

## Credits:

See http://klen.github.io/py-frameworks-bench.


## Contributors

* Amber Brown (https://github.com/hawkowl)
* Giovanni Barillari (https://github.com/gi0baro)
* Kirill Klenov (https://github.com/klen)
