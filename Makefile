#DHOST	    ?= 192.168.99.100
DHOST	    ?= 127.0.0.1
VIRTUAL_ENV ?= .env


$(VIRTUAL_ENV)/bin/py.test: $(VIRTUAL_ENV) $(CURDIR)/requirements.txt
	@$(VIRTUAL_ENV)/bin/pip install -r $(CURDIR)/requirements.txt
	@touch $(CURDIR)/requirements.txt
	@touch $(VIRTUAL_ENV)/bin/py.test

.PHONY: db
db: $(VIRTUAL_ENV)/bin/py.test
	@echo Fill DATABASE
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/python db.py

.PHONY: docker
docker:
	docker build -t horneds/pybenchmark $(CURDIR)

RUN ?=
.PHONY: docker-run
docker-run:
	docker run --net=host --name=benchmark -d horneds/pybenchmark $(RUN)

test: $(VIRTUAL_ENV)/bin/py.test
	$(VIRTUAL_ENV)/bin/py.test -xs tests.py


WRK = wrk -d20s -c200 -t10 --timeout 10s -s scripts/cvs-report.lua
bench: $(VIRTUAL_ENV)
	@rm -f $(CURDIR)/results.csv
	@echo title,min,50%,75%,90%,99%,99.9%,max,mean,duration,reqs,err,read err,timeouts > $(CURDIR)/results.csv
	# aiohttp
		@make aiohttp OPTS="-p pid -D -w 2"
		@sleep 2
		@make wrk TESTEE=aiohttp
		@kill `cat $(CURDIR)/pid`
		@sleep 5
	# # bottle
	# 	# @make bottle OPTS="-p pid -D -w 2"
	# 	# @sleep 2
	# 	# @make wrk TESTEE=bottle
	# 	# @kill `cat $(CURDIR)/pid`
	# 	# @sleep 3
	# wsgi
		@make wsgi OPTS="-p pid -D -w 2"
		@sleep 3
		@make wrk TESTEE=wsgi
		@kill `cat $(CURDIR)/pid`
		@sleep 5
	# django
		@make django OPTS="-p pid -D -w 2"
		@sleep 2
		@make wrk TESTEE=django
		@kill `cat $(CURDIR)/pid`
		@sleep 5
	# # # falcon
	# # 	# @make falcon OPTS="-p pid -D -w 2"
	# # 	# @sleep 2
	# # 	# @make wrk TESTEE=falcon
	# # 	# @kill `cat $(CURDIR)/pid`
	# # 	# @sleep 3
	# # pyramid
	# 	# @make pyramid OPTS="-p pid -D -w 2"
	# 	# @sleep 2
	# 	# @make wrk TESTEE=pyramid
	# 	# @kill `cat $(CURDIR)/pid`
	# 	# @sleep 3
	# flask
		@make flask OPTS="-p pid -D -w 2"
		@sleep 2
		@make wrk TESTEE=flask
		@kill `cat $(CURDIR)/pid`
		@sleep 5
	# sanic
		@make sanic OPTS="-p pid -D -w 2"
		@sleep 2
		@make wrk TESTEE=sanic
		@kill `cat $(CURDIR)/pid`
		# It may take several seconds to shootdown...
		@sleep 5
	# tornado
		@make tornado
		@sleep 2
		@make wrk TESTEE=tornado
		@kill `cat $(CURDIR)/pid`
		@sleep 5


TESTEE = ""
wrk:
	# TESTEE=$(TESTEE) $(WRK) http://127.0.0.1:5000/json
	# TESTEE=$(TESTEE) $(WRK) http://127.0.0.1:5000/remote
	TESTEE=$(TESTEE) $(WRK) http://127.0.0.1:5000/complete

OPTS =
aiohttp: $(VIRTUAL_ENV)
	@echo $(CURDIR)
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k aiohttp.worker.GunicornWebWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/aiohttp

bottle: $(VIRTUAL_ENV)
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/bottle

django: $(VIRTUAL_ENV)
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/django

falcon: $(VIRTUAL_ENV)
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/falcon

flask: $(VIRTUAL_ENV)
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/flask

pyramid:
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/pyramid

tornado:
	cd frameworks/tornado && $(VIRTUAL_ENV)/bin/python app.py & echo "$$!" > pid

wsgi:
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
	    -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
	    --chdir=$(CURDIR)/frameworks/wsgi

sanic:
	@DHOST=$(DHOST) $(VIRTUAL_ENV)/bin/gunicorn app:app $(OPTS) \
		-k sanic.worker.GunicornWorker --bind=127.0.0.1:5000 \
		--chdir=$(CURDIR)/frameworks/sanic