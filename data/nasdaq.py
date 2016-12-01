from trading.page import SymbolPage
from trading.data import _Quotes
from trading import parser
from trading import util

# #ifndef VERSION_SPIDER
class ShortInterest_Entry(object):
    def __init__(self, date, shares, avg_vol, ratio):
        self.date = date
        self.shares = shares
        self.avg_vol = avg_vol
        self.ratio = ratio

    def __str__(self):
        return ";".join([self.date.date_str(), 
                         str(self.shares), 
                         str(self.avg_vol), 
                         str(self.ratio)])

    __repr__ = __str__
# #endif

class ShortInterest(SymbolPage):
    # don't inherit from list -> __cmp__ will be fscked up!
    CachePrefix = "nasdaq_short_interest"
    _URL = "http://www.nasdaq.com/asp/quotes_full.asp?mode=&kind=shortint&selected=%s"

# #ifndef VERSION_SPIDER
    Entry = ShortInterest_Entry

    def __init__(self, cache_dir, name):
        super(ShortInterest, self).__init__(cache_dir, name)
        self.data = []

    def _sanitize(self, data):
        return data.replace("\>", "/>")

    def _init(self, data):
        #XXX add testcase: SKFRF (unknown symbol)
        #XXX add testcase: ATLKY (Short Interest not available)
        if data.find('is an unknown symbol.') != -1 or \
           data.find('Short Interest Not available for') != -1:
            self.valid = False
            return
        p = parser.parse(data)
        raw_table = p.find('table', attrs={'id':'ShortInterest1_ShortInterestGrid'})
        if raw_table is None: #XXX add testcase: AMAG
            self.valid = False 
            return
        table = parser.tablify(raw_table)
        assert table[0][0].startswith('Settlement Date')
        assert table[0][1].startswith('Short Interest')
        for line in table[2:]:
            date, short, avg_vol, short_ratio = line
            short = util.atoi(short)
            avg_vol = util.atoi(avg_vol)
            if short_ratio == 'N/A':
                short_ratio = None
            else:
                short_ratio = float(short_ratio)
            date = util.Date(date)
            self.data.append(self.Entry(date, short, avg_vol, short_ratio))
# #endif

class TimesSales(_Quotes):
    CachePrefix = "nasdaq_times_sales"
    _URL = 'http://www.nasdaq.com/aspx/NLS/NLSHandler.ashx?msg=MIN&Symbol=%s'
    CacheExtension = "xml"

    def __init__(self, cache_dir, name, date):
        super(_Quotes, self).__init__(cache_dir, name)
        self._date = util.Date(date)

    def _init(self, data):
        p = parser.parse(data)
        result = {}
        prev = None
        for e in p.findAll('min'):
            ticks = long(e.time.string)/1000
            h = int(ticks / 3600)
            m = int((ticks - h*3600.) / 60)
            s = (ticks - h*3600. - m*60.) / 60.
            amount = int(e.shares.string)
            price = float(e.price.string)
            d = util.Date("%s %02d:%02d:%.2f" % (self._date.date_str(), h, m, s))
            e = self.Entry(d, price, price, price, price, amount)
            result[d] = e
            e.prev = prev
            if prev:
                prev.next = e
            prev = e
        self.data = result

    def get(self, date, skip_min=0):
        # check if date is the same date as dates in self.data
        if self.data:
            if date.date_str() != self.data.keys()[0].date_str():
                return None
        d = (date.timedelta() + skip_min*60)
        keys = self.data.keys()
        keys.sort()
        k = filter(lambda x: x.timedelta() >= d, keys)
        return k and self.data[min(k)] or None

class RealTime(SymbolPage):
    _URL = "http://www.nasdaq.com/aspx/nasdaqlastsale.aspx?selected=%s"
