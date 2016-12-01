from trading.page import SymbolPage, _Page
from trading.data import _Schedule
from trading import parser
from trading import util
from decimal import Decimal
from mx.DateTime import TimeDelta

import re
import os

# #ifndef VERSION_SPIDER
_period_pat = re.compile('^Q[1234]{1}\s+\d{4}$')
def parse_period(period) :
    if not _period_pat.match(period) :
        return None, None
    q, y = period.split()
    return int(q[-1]), int(y)

def parse_money(text) :
    text = text.strip()
    if text.lower() == 'n/a':
        return None
    amount = text[2:].strip()
    if text.startswith('-'):
        return Decimal("-" + amount)
    return Decimal(amount)
# #endif

class Schedule(_Schedule):
    CachePrefix = "earnings_schedule"
    Filename = 'earnings_schedule.txt'
    _URL = "http://www.earnings.com/earning.asp?date=%s&sortby=startdate&client=cb"
    #_URL = "http://thestreet.ccbn.com/earning.asp?date=%s&sortby=startdate&client=cb"

    ValidSymbolPat = re.compile("^[a-z]*[A-Z]*$")

    def _init(self, data):
        p = parser.parse(data)
        schedule = p.find('b', text='Earnings Releases - Confirmed').findNext('table')
        schedule = parser.tablify(schedule)
        if schedule != [[u'There are no events to display.']]:
            assert schedule[0] == [u'', u'SYMBOL', u'COMPANY', u'EVENT TITLE', u'EPS ESTIMATE', u'EPS ACTUAL', u'PREV. YEAR ACTUAL', u'DATE/TIME (ET)']
            assert schedule[-1] == ['']
            for r in schedule[1:-1]:
                s, (bmo, amc, d) = str(r[1]), util.parse_earnings_date(str(r[-1]))
                d = util.Date(self.date.date_str() + " %s" % d.strftime("%H:%M"))
                assert d.date_str() == self.date.date_str()
                e = Schedule.Entry(s, d, bmo, amc)
                if self.ValidSymbolPat.match(s):
                    self.data.append(e)

# #ifndef VERSION_SPIDER
class History_Entry(object):
    def __init__ (self, y, q, est, act, year_ago, date, bmo, amc, title) :
        assert not (bmo and amc)
        self.year = y
        self.quarter = q
        self.est = est
        self.act = act
        self.year_ago = year_ago
        self.date = date
        self.bmo = bmo
        self.amc = amc
        self.title = title
        self.next = None
        self.prev = None

    def quote(self, quotes, tries=10):
        d = self.date.date_obj()
        q = quotes.get(d)
        while q is None and tries:
            print "%s: quote for %s not found, trying %s" % \
                (quotes.name, d.datetime_str(), (d+1).date_str())
            tries -= 1 
            d = d + 1 #XXX ci minus?
            q = quotes.get(d)
        return q

    def reaction(self, quotes): #XXX nejak unifikovat s tools.cache?
        q = self.quote(quotes)
        if q is None or q.next is None or q.prev is None:
            return None
        if self.amc:
            r = q.next.open/q.close
        elif self.bmo:
            r = q.open/q.prev.close
        else:
            d = self.date.timedelta()
            if d < TimeDelta(hours=16) and d > TimeDelta(hours=9, minutes=30):
                r = q.close/q.open
            else:
                r = q.next.open/q.prev.close
        return (r-1) * 100

    def when_str(self):
        if self.date.has_time():
            result = self.date.datetime_str()
        else:
            result = self.date.date_str()
            if self.amc:
                result = '%s AMC' % result
            elif self.bmo:
                result = '%s BMO' % result
        return result

    def raw_date(self):
        result = self.date.date_str()
        if self.date.strftime('%H:%M') != '00:00':
            return self.date.datetime_str()
        if self.bmo:
            return "%s BMO" % result 
        elif self.amc:
            return "%s AMC" % result 
        return result

    def period(self, fmt="Q%d %d"):
        if not (self.quarter and self.year):
            return None
        return fmt % (self.quarter, self.year)

    def __str__(self):
        return ";".join(map(str, [self.year,self.quarter, self.est, 
                                  self.act, self.date, self.bmo, 
                                  self.amc, self.title]))
    __repr__ = __str__
# #endif

class History(SymbolPage): 
    CachePrefix = "earnings_history"

    #_URL = "http://thestreet.ccbn.com/company.asp?client=cb&ticker=%s"
    _URL = "http://www.earnings.com/company.asp?client=cb&ticker=%s"

# #ifndef VERSION_SPIDER
    Entry = History_Entry
# #endif

    def __init__(self, cache_dir, name):
        super(History, self).__init__(cache_dir, name)
        self.data = []

# #ifndef VERSION_SPIDER
    def next(self, now=None):
        now = now or util.now().date_obj()
        data = filter(lambda x: x.date is not None and x.date >= now, self.data)
        if not data:
            return
        return data[-1] #XXX add UNITTEST: pred tym tu bola 0, co je u stockov s schedule na rok dopredu? 

    def last(self, date):
        result = None
        data = filter(lambda x:x.date is not None and x.date < date, self.data)
        if data:
            result = data[0]
        return result

    def _init(self, data):
        p = parser.parse(data)
        earnings = p.find('b', text='Earnings Releases')
        if earnings is None:
            self.valid = False
            return
        earnings = p.find('b', text='Earnings Releases').findNext('table')
        earnings = parser.tablify(earnings)
        assert earnings and earnings[0] == ['SYMBOL', 'PERIOD', 'EVENT TITLE', 'EPS ESTIMATE', 'EPS ACTUAL', 'PREV. YEAR ACTUAL', 'DATE/TIME (ET)']
        earnings = filter(lambda x : len(x) == 7, earnings[1:])
        next = None
        for row in earnings:
            period, title, est, act, year_ago, date = row[1:]
            q, y = parse_period(period)
            est = parse_money(est)
            act = parse_money(act)
            year_ago = parse_money(year_ago)
            bmo, amc, date = util.parse_earnings_date(date)
            e = self.Entry(y, q, est, act, year_ago, date, bmo, amc, title)
            e.next = next
            if e.next:
                e.next.prev = e
            next = e
            #print e
            self.data.append(e)
# #endif
