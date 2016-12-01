from trading.page import SymbolPage, _Page
from trading import util
from mx.DateTime import TimeDelta

# #ifndef VERSION_SPIDER
class Quotes_Entry(object):
    def __init__(self, date, open, high, low, close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.prev = None
        self.next = None

    def typical_price(self):
        return (self.high + self.low + self.close) / 3

    def highest_close(self, period):
        i = 0
        result = self.close
        start = self
        while i < period:
            start = start.prev
            if start is None:
                break
            if start.close > result:
                result = start.close
            i += 1
        return result

    def lowest_close(self, period):
        i = 0
        result = self.close
        start = self
        while i < period:
            start = start.prev
            if start is None:
                break
            if start.close < result:
                result = start.close
            i += 1
        return result

    def willr(self, period=14):
        return (self.highest_close(period) - self.close) / \
               (self.highest_close(period) - self.lowest_close(period)) * 100

    def high_low_range(self, period=120):
        high = self.highest_close(period=period)
        low = self.lowest_close(period=period)
        if high-low:
            return (100/(high-low))*(self.close-low)

    def cci(self, period=20):
        smatp = self.ma(period)
        if smatp is None:
            return None
        data = []
        q = self
        for i in range(period):
            data.append(abs(smatp - q.typical_price()))
            if q.prev is not None:
                q = q.prev
            else:
                util.debug("data.Quotes_Entry.cci: not enough data available")
                return None
        sd = float(sum(data)/period)
        if not sd:
            return None
        return (float(self.typical_price()) - float(smatp)) / (0.015 * sd)

    def ma(self, period):
        data = []
        q = self
        for i in range(period):
            data.append(q.typical_price())
            if q.prev is not None:
                q = q.prev
            else:
                util.debug("data.Quotes_Entry.ma: not enough data available")
                return None
        return util.ma(data)

    def __str__(self):
        return ",".join(map(str, [self.date.datetime_str(), self.open,
                                  self.high, self.low, self.close,
                                  self.volume]))
    __repr__ = __str__
# #endif

class _Quotes(SymbolPage):
    CacheExtension = "csv"

# #ifndef VERSION_SPIDER
    Entry = Quotes_Entry

    def __init__(self, *args, **kw):
        super(_Quotes, self).__init__(*args, **kw)
        self.data = {}

    def last(self):
        if not self.data:
            return
        k = max(self.data.keys())
        return self.data[k]

    def first(self):
        if not self.data:
            return
        k = min(self.data.keys())
        return self.data[k]

    def get(self, date, default=None):
        raise NotImplementedError

    def prev_close(self, date):
        date = util.Date(date)
        prev = date
        if date.timedelta() <= TimeDelta(hours=15, minutes=59):
            prev = util.prev_trading_day(date)
        return self.get("%s 15:59:00" % prev.date_str())

    def next_open(self, date):
        date = util.Date(date)
        next = date
        if date.timedelta() >= TimeDelta(hours=9, minutes=30):
            next = util.next_trading_day(date)
        return self.get("%s 09:30:00" % next.date_str())
# #endif

class _Insiders_Entry(object):
    def __init__(self, date, name, title, link, type, shares, value=None):
        self.date = date
        self.name = name
        self.title = title
        self.link = link
        self.type = type
        self.shares = shares
        self.value = value

    def priority(self):
        raise NotImplementedError

    def __str__(self):
        return ":".join(map(str, [self.date.date_str(),
                                  self.name,
                                  self.shares,
                                  self.type]))
    __repr__ = __str__

class Schedule_Entry(object):
    Sep = ';'

    def __init__(self, symbol, date, bmo, amc, confirmed=True):
        self.symbol = symbol
        self.date = date
        self.bmo = bmo
        self.amc = amc
        self.confirmed = confirmed
        assert not (self.bmo and self.amc)

    def is_intraday(self):
        if self.date.hour or self.date.minute:
            when = self.date.hour*60 + self.date.minute
            if when >= 9*60+30 or when <= 16*60+30:
                return True
        return False

    def __str__(self):  
        args = [self.symbol]
        when = (self.amc and "AMC") or (self.bmo and "BMO") \
            or self.date.strftime("%H:%M")
        if when == "00:00":
            when = ""
        else:
            when = " %s" % when # add a space
        args.append(self.date.date_str() + when)
        result = self.Sep.join(args)
        if not self.confirmed:
            result += " *"
        return result

    __repr__ = __str__

class _Schedule(_Page):
    CachePrefix = None
    Filename = None
    DateFmt = "%Y%m%d"

    CacheExtension = 'html'
    Entry = Schedule_Entry

    def __init__(self, archive, date):
        super(_Schedule, self).__init__(archive)
        self.date = util.Date(date)
        self.data = []
        assert self.CachePrefix is not None, "set Schedule.CachePrefix"
        assert self.Filename is not None, "set Schedule.Filename"

    def init(self, data=None, force=False):
        if force or not self.initialized:
            if not data:
                assert self.is_cached(), "not cached"
                a = util.ZipFile(self.archive, mode='r')
                data = a.read(self.cache_fn())
                a.close()
            self._validate(data, None)
            if self.valid:
                self._init(data)
            self.initialized = True

    def cache_fn(self):
        return "%s.%s" % (self.CachePrefix, self.CacheExtension)

    def url(self):
        return self._URL % self.date.strftime(self.DateFmt)

    def save(self, archive):
        data = "\n".join(map(str, self.data))
        util.ZipFile.Replace(archive, self.Filename, data)
        print "Saved schedule to: %s" % self.Filename

    def Load(cls, archive):
        result = []
        try:
            a = util.ZipFile(archive)
            data = a.read(cls.Filename)
            a.close()
        except (IOError, KeyError): # zip doesn't exist/not found
            return result
        for line in data.splitlines():
            line = line.strip()
            symbol, date = line.split(cls.Entry.Sep)[:2]
            bmo, amc, date = util.parse_earnings_date(date)
            e = cls.Entry(symbol, date, bmo, amc)
            result.append(e)
        return result
    Load = classmethod(Load)

    def Merge(*datasets):
        result = []
        seen = []
        for data in datasets:
            for e in data:
                if e.symbol not in seen:
                    result.append(e)
                    seen.append(e.symbol)
        return result
    Merge = staticmethod(Merge)


class Estimates_Period:
    "Estimate of an quarter/year"

    def __init__ (self, eps=None, rev=None):
        self.eps = self._parse_eps(eps)
        self.rev = self._parse_rev(rev)

    def _parse_eps(self, eps):
        return util.atof(eps)

    def _parse_rev(self, rev):
        return  util.atof(rev)
