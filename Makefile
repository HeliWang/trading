DB_DIR = $(shell python -c "from trading import config; print config.DB_DIR")

rsync_to_diesel:
	rsync -e ssh -ai ${DB_DIR} diesel:

rsync_from_diesel:
	rsync -e ssh -ai diesel:${DB_DIR} ~

unittest:
	python2.4 parser.py
	python2.4 util.py
	python2.4 htmlgen.py
	trial2.4 trading.test

edb_txt:
	find $(DB_DIR) -name '*_-1.zip' > ~/edb.txt

backup:
	rm -f ~/edb_backup.tar
	tar cf ~/edb_backup.tar $(DB_DIR)

clean:
	find -name '*.pyc' -exec rm {} \;
	rm -rf _trial_temp
	rm -rf spider
	rm -f spider.tar

SPIDER_DIR = ./spider
spider:
	rm -rfvi ${SPIDER_DIR} || exit 0
	python tools/gen_version.py ${SPIDER_DIR} VERSION_SPIDER \
		__init__.py \
		holidays.txt \
		browser.py \
		config.py \
		page.py \
		parser.py \
		util.py \
		data/__init__.py \
		data/clearstation.py \
		data/earnings.py \
		data/lycos.py \
		data/marketwatch.py \
		data/msn.py \
		data/nasdaq.py \
		data/quote.py \
		data/reuters.py \
		data/schaeffersresearch.py \
		data/stockta.py \
		data/yahoo.py \
		tools/__init__.py \
		tools/schedule.py \
		tools/fetch.py
	cp -v ../sgmllib.py ${SPIDER_DIR}
	cp -v /usr/share/python-support/beautifulsoup/BeautifulSoup.py ${SPIDER_DIR}
	cp -v /usr/lib/python2.4/site-packages/ClientForm.py ${SPIDER_DIR}
	cp -v /usr/lib/python2.4/site-packages/pullparser.py ${SPIDER_DIR}
	cp -rv /usr/lib/python2.4/site-packages/mechanize ${SPIDER_DIR}
	cp -rv /usr/lib/python2.4/site-packages/ClientCookie ${SPIDER_DIR}
	find ${SPIDER_DIR} -name '*py' | xargs sed -i 's/from trading/from spider/g'
	find ${SPIDER_DIR} -name '*py' | xargs sed -i 's/from spider //g'
	find ${SPIDER_DIR} -name '*py' | xargs sed -i 's/from spider./from /g'
	python -c 'import compileall; compileall.compile_dir("${SPIDER_DIR}", force=1)'
	find ${SPIDER_DIR} -name '*py' | xargs rm -v
	tar cf spider.tar ${SPIDER_DIR}
