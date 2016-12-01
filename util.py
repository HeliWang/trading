from mx.DateTime import DateTimeFrom, TimeDelta
from datetime import datetime
from trading import config
from decimal import Decimal

import os
import time
import urllib
import re
import stat
import zipfile
import tempfile
import shutil

class ZipFile(zipfile.ZipFile):

    def __init__(self, file, mode="r", compression=zipfile.ZIP_DEFLATED):
        zipfile.ZipFile.__init__(self, file, mode=mode, compression=compression)

    def Replace(archive_fn, fn, data, compression=zipfile.ZIP_DEFLATED):
        archive = ZipFile(archive_fn, mode='r')
        fd, tmpfn = tempfile.mkstemp()
        tmp = ZipFile(tmpfn, mode='w', compression=compression)
        for e in archive.filelist:
            if e.filename == fn:
                continue
            tmp.writestr(e.filename, archive.read(e.filename))
        if data is not None:
            tmp.writestr(fn, data)
        tmp.close()
        archive.close()
        shutil.move(tmpfn, archive_fn)
        os.close(fd)
    Replace = staticmethod(Replace)

    def Remove(archive_fn, fn, compression=zipfile.ZIP_DEFLATED):
        ZipFile.Replace(archive_fn, fn, None, compression=compression)
    Remove = staticmethod(Remove)


def ma(data):
    """
    >>> ma(range(100))
    Decimal("49.5")
    >>> ma([1,2])
    Decimal("1.5")
    """
    return sum(data)/Decimal(len(data))

def debug(what):
    if config.DEBUG:
        print what

def flatten(*seqs):
    """
    >>> flatten([], [])
    []
    >>> flatten([5], [1,3])
    [5, 1, 3]
    """
    result = []
    for s in seqs:
        result.extend(list(s))
    return result

# http://dynamic.nasdaq.com/dynamic/afterhourmanyse.stm
def parse_earnings_date(date_str):
# #ifndef VERSION_SPIDER
    """
    >>> parse_earnings_date("1.1.2005 7:00")
    (True, False, Date('2005-01-01 07:00:00'))
    >>> parse_earnings_date("1-Aug-2005 10:00")
    (False, False, Date('2005-08-01 10:00:00'))
    >>> parse_earnings_date("1.1.2005 16:00")
    (False, False, Date('2005-01-01 16:00:00'))
    >>> parse_earnings_date("1.1.2005 16:01")
    (False, True, Date('2005-01-01 16:01:00'))
    >>> parse_earnings_date("1.1.2005")
    (False, False, Date('2005-01-01 00:00:00'))
    >>> bmo, amc, _ = parse_earnings_date("12-Jul")
    >>> bmo, amc
    (False, False)
    >>> bmo, amc, _ = parse_earnings_date("12-Jul AMC")
    >>> bmo, amc
    (False, True)
    >>> bmo, amc, _ = parse_earnings_date("12-Jul BMO")
    >>> bmo, amc
    (True, False)
    >>> bmo, amc, _ = parse_earnings_date("12-Jul 2:30 AM")
    >>> bmo, amc
    (True, False)
    >>>
    """
# #endif
    if date_str.find(" - ") != -1: #date1 - date2
        return False, False, None
    bmo = date_str.endswith(" BMO") and 1 or 0
    amc = date_str.endswith(" AMC") and 1 or 0
    if bmo or amc :
        date_str = date_str[:-4]
    date = Date(date_str)
    delta = float(date.diff(date.date_obj()))
    if delta :
        if delta < 3600 * 9.5 :
            bmo = 1
        elif delta > 3600 * 16 :
            amc = 1
    assert not (bmo and amc), date_str
    return bool(bmo), bool(amc), date

def mkdir(dirname):
    try :
        os.mkdir(dirname)
    except OSError:
        pass

def atof(text) :
# #ifndef VERSION_SPIDER
    """
    >>> atof("2.01K")
    2009.9999999999998
    >>> atof("2M")
    2000000.0
    >>> atof("10.32134B")
    10321340000.0
    >>> atof("1")
    1.0
    >>> atof("5,100")
    5100.0
    >>> atof(10.15)
    10.15
    >>> atof("") == atof(None)
    True
    """
# #endif
    if text in ("", "N/A", None, "None"): #XXX remove "None"
        return 
    text = str(text).replace(',', '')
    _value = text[:-1]
    if text.endswith("B") :
        return float(_value) * 1000000000
    elif text.endswith("T") :
        return float(_value) * 1000000000000
    elif text.endswith("M") :
        return float(_value) * 1000000
    elif text.endswith("K") :
        return float(_value) * 1000
    else :
        return float(text)

def atoi(text):
# #ifndef VERSION_SPIDER
    """
    >>> atoi(231.1)
    231
    >>> atoi('231,011.1K')
    231011100
    >>> atoi('-3,121')
    -3121
    >>> atoi('0')
    0
    """
# #endif
    val = atof(text)
    if val is not None:
        return int(val)

class Date:
# #ifndef VERSION_SPIDER
    """
    >>> date = Date(u"01.01.2006")
    >>> date
    Date('2006-01-01 00:00:00')
    >>> date.datetime_str()
    '2006-01-01 00:00:00'
    >>> date + 14
    Date('2006-01-15 00:00:00')
    >>> date - 1 
    Date('2005-12-31 00:00:00')
    >>> date.has_time()
    False
    >>> date < date + 1
    True
    >>>
    >>> Date("22-Jul-03 12:30:20 PM").strftime("%x %X")
    '07/22/03 12:30:20'
    >>> Date("22-Jul-03 12:30:20 PM").date_obj().strftime('%x %X')
    '07/22/03 00:00:00'
    >>> Date('22-Jul-03 12:00 PM') == Date('22-Jul-03 12:00 PM')  
    True
    >>> Date("10.1.2005").diff(Date("1.1.2005")).tuple()
    (9, 0, 0, 0.0)
    >>> Date('12:00pm 06/28/06').datetime_str()
    '2006-06-28 12:00:00'
    >>> Date('12:00pm 06/28/06').has_time()
    True
    """
# #endif

    def __init__ (self, value) :
        assert value is not None
        if type(value) is unicode: #XXX
            value = str(value)
        if hasattr(value, 'strftime') :
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        if type(value) is str:
            i1 = value.find('12:')
            i2 = value.upper().find('PM')
            if (i1 != -1 and i2 != -1) and i1 < i2:
                value = value.upper().replace('PM', '')
        self.raw = DateTimeFrom(value)

    def datetime_str(self):
        return self.raw.strftime('%Y-%m-%d %H:%M:%S')

    def timedelta(self):
        return TimeDelta(hours=self.hour, 
                         minutes=self.minute, 
                         seconds=self.second)

    def next_week(self):
        """
        >>> Date('10.7.2006').next_week()
        Date('2006-07-17 00:00:00')
        >>> Date('14.7.2006').next_week()
        Date('2006-07-17 00:00:00')
        """
        week = int(self.strftime('%W'))
        next = self
        while week == int(next.strftime('%W')):
            next += 1
        return next

    def date_str(self):
        return self.raw.strftime('%Y-%m-%d')

    def has_time(self):
        return not self.strftime("%H:%M") == "00:00" 

    def __str__ (self) :
        return "Date('%s')" % self.datetime_str()

    def datetime(self):
        return datetime.fromtimestamp(float(self))

    __repr__ = __str__

    def __getstate__(self):
        return float(self)

    def __setstate__(self, f):
        self.raw = DateTimeFrom(f)

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def __cmp__ (self, other) :
        return cmp(self.raw, Date(other).raw)

    def __add__ (self, i) :
        return Date(self.raw + i)

    def __sub__ (self, i) :
        return Date(self.raw - i)

    def __float__ (self) :
        return float(self.raw)

    def diff(self, date) :
        return self.raw - date.raw

    def date_obj(self):
        return Date(self.date_str())

    def is_workday(self):
        """
        >>> Date('17.7.2006').is_workday()
        True
        >>> Date('16.7.2006').is_workday()
        False
        >>> Date('15.7.2006').is_workday()
        False
        >>> Date('14.7.2006').is_workday()
        True
        """
        return int(self.strftime("%u")) in [1, 2, 3, 4, 5]

    def __hash__(self):
        return hash(self.raw)

def now():
    return Date(time.time())

def _holidays():
    fn = os.path.split(__file__)[0]
    fn = os.path.join(fn, 'holidays.txt')
    result = []
    for line in open(fn).readlines():
        date = Date(line.strip())
        result.append(date.date_obj())
    return result

holidays = _holidays()

def is_trading_day(date):
    """
    >>> is_trading_day('23.11.2006')
    False
    >>> is_trading_day('22.11.2006')
    True
    """
    date = Date(date)
    if date.date_obj() not in holidays and date.is_workday():
        return True
    return False

def next_trading_day(date):
    """
    >>> next_trading_day('22.11.2006')
    Date('2006-11-24 00:00:00')
    >>> next_trading_day('23.11.2006')
    Date('2006-11-24 00:00:00')
    """
    date = Date(date)
    while 1:
        date += 1
        if is_trading_day(date):
            return date

def prev_trading_day(date):
    """
    >>> prev_trading_day('23.11.2006')
    Date('2006-11-22 00:00:00')
    """
    date = Date(date)
    while 1:
        date -= 1
        if is_trading_day(date):
            return date

# #ifndef VERSION_SPIDER
date_pat = re.compile('^\d{4}-\d{2}-\d{2}$')

def quantile(lst, f=0.5):
    """Returns the f%-quantile of a list. Returns the median for f=0.5"""
    # idea from: http://en.literateprograms.org/MedianFilter_(Python)
    lst = sorted(lst)
    i = int(len(lst)*f)
    return lst[min(len(lst)-1, i)]

def pct(base, rest):
    """
    >>> pct(5, 5)
    0.0
    """
    return float(rest)/float(base)*100-100

def pct_str(base, rest):
    """
    >>> pct_str(5, 10)
    '100.00%'
    >>> pct_str(5, -1)
    '-120.00%'
    """
    return "%.2f%%" % pct(base, rest)

def cache_page(cache, k, cls, dir, *args):
    key = "%s:%s" %(k, dir)
    if cache.has_key(key):
        return cache[key]
    val = cls(dir, *args)
    cache[key] = val
    val.init()
    return val

def fmt_number(number):
    if number is None:
        return None
    result = []
    a = str(number)
    b = ""
    if a.find('.') != -1:
        a, b = a.split('.')
        b = ".%s" % b
    while 1:
        i = a[-3:]
        if not i:
            break
        result.insert(0, i)
        a = a[:-3]
    return ",".join(result) + b

def mean(seq, geometric=False):
    """
    >>> mean([1])
    1.0
    >>> mean([1, 2])
    1.5
    >>> mean([1, 2, 2, 4, 5])
    2.7999999999999998
    >>> mean([1,2,3,-4], geometric=1) == (1.01*1.02*1.03*.96-1)*100
    True
    >>> 
    """
    if not seq:
        return None
    if geometric:
        return (reduce(lambda x, y: x*y, map(lambda x: (x+100.)/100, seq))-1)*100
    return float(sum(seq))/len(seq)

def median(seq):
    """
    >>> median([1])
    1.0
    >>> median([1,2])
    1.5
    >>> median([1,2,3,4,1,1,1,1,4,2,8])
    2.0
    """
    if not seq:
        return None
    seq = list(seq)
    seq.sort()
    if len(seq) % 2:
        return float(seq[len(seq)/2])
    else:
        m = len(seq)/2
        return float(seq[m-1] + seq[m])/2.

def mode(seq):
    """
    >>> mode([1])
    (1, 1)
    >>> mode([1,2])
    (2, 1)
    >>> mode([1,2,1])
    (1, 2)
    >>> mode([1,2,1,2,1,1,4,7])
    (1, 4)
    """
    if not seq:
        return None
    d = {}
    for s in seq:
        if not d.has_key(s):
            d[s] = 1
        else:
            d[s] += 1
    items = d.items()
    items.sort(lambda x, y: cmp(x[1], y[1]))
    return items[-1]

def rstats(seq):
    if not seq:
        return None
    return min(seq), quantile(seq, f=.25), median(seq), mean(seq), \
           quantile(seq, f=.75), max(seq)

def split_every(seq, n):
    """
    >>> split_every(range(10), 2)
    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    >>> split_every(range(10), 3)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    result = []
    while seq:
        slice = seq[:n]
        seq = seq[n:]
        result.append(slice)
    return result

def lstrip(string, pattern):
    """
    >>> lstrip("foobar", "foo")
    'bar'
    >>> lstrip("foobar", "baz")
    'foobar'
    """
    if string.startswith(pattern):
        return string[len(pattern):]
    return string

def unique(seq):
    """
    >>> unique([1, 2, 1, 2, 2, 1])
    [1, 2]
    """
    d = {}
    for e in seq:
        d[e] = None
    return d.keys()

def unlink(what):
    try :
        os.unlink(what)
    except OSError:
        pass

def transpose(matrix):
    """
    >>> m = range(3), range(3), range(3)
    >>> m
    ([0, 1, 2], [0, 1, 2], [0, 1, 2])
    >>> transpose(m)
    [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    >>>
    """
    return zip(*matrix)

def from_to_parser(parser=None, usage="%prog [options] arguments"):
    from optparse import OptionParser
    p = parser or OptionParser(usage=usage)
    p.add_option('-d', '--db_dir', default=config.DB_DIR)
    p.add_option('-b', '--begin_date')
    p.add_option('-e', '--end_date')
    return p

def db_dates(root_dir=config.DB_DIR, begin=None, end=None):
    begin = begin and Date(begin) or None
    end = end and Date(end) or None
    dates = os.listdir(root_dir)
    dates = filter(lambda d: date_pat.match(d) and 
                             os.path.isdir(os.path.join(root_dir, d)), dates)
    dates.sort(lambda x, y: cmp(Date(x), Date(y)))
    if begin:
        dates = filter(lambda x: x >= begin, dates)
    if end:
        dates = filter(lambda x: x <= end, dates)
    return dates

def db_date_symbols(db_date, root_dir=config.DB_DIR, day="-1", abs=False):
    symbols = os.listdir(os.path.join(root_dir, db_date))
    symbols = filter(lambda x:x.endswith("_%s.zip" % day), symbols)
    if abs:
        symbols = map(lambda x: os.path.join(root_dir, db_date, x), symbols)
    return symbols


if __name__ == "__main__" :
    import doctest, util
    doctest.testmod(util)
# #endif
