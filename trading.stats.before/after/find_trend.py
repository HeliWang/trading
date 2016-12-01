from mx.DateTime import TimeDelta
from trading.tools.cache import Cache
from trading.data import yahoo, quote
from trading import util
from trading import config

import os

def cross(q, long, *timeframes):
    if long:
        comp = lambda a, b: a > b
    else:
        comp = lambda a, b: a < b
    while filter(lambda x: comp(q.close, q.ma(x)), timeframes):
        q = q.next
        #print map(lambda x: "%.2f" % q.ma(x), timeframes), q.close, q.date.datetime_str()
        if q is None:
            break
    return q

if __name__ == "__main__" :
    from optparse import OptionParser

    usage = "%prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--begin_date')
    parser.add_option('-e', '--end_date')
    parser.add_option('-w', '--when', default="bai")
    parser.add_option('-g', '--min_gain', default=2, type="int")
    #XXX implicit 0-9min
    #parser.add_option('-r', '--reaction_time', default=5, type="int")
    #parser.add_option('-p', '--min_position', default=5000, type="int")
    opts, args = parser.parse_args()

    cache = Cache()
    cache.load_all()

    symbols = []
    total = 0
    db_dir = config.DB_DIR
    for d in util.db_entries(root_dir=db_dir):
        date = util.Date(d)
        #XXX factorize a filter object
        if opts.begin_date and util.Date(opts.begin_date) > date:
            continue
        if opts.end_date and util.Date(opts.end_date) <= date:
            continue
        for symbol in util.db_entry_symbols(db_dir, d):
            result = cache.get(date, symbol)
            if result is None:
                print "%s: no result" % symbol
                continue
            if result.gain is None or result.gain2 is None:
                print "%s: no gain(s)" % symbol
                continue
            d = result.rel_date.timedelta()
            if not 'b' in opts.when:
                if d < TimeDelta(hours=9, minutes=30):
                    continue
            if not 'i' in opts.when:
                if d >= TimeDelta(hours=9, minutes=30) and \
                   d < TimeDelta(hours=16, minutes=0):
                    continue
            if not 'a' in opts.when:
                if d >= TimeDelta(hours=16, minutes=0):
                    continue

            dir = os.path.join(config.DB_DIR, date.date_str(), symbol, '-1')
            dir3 = os.path.join(config.DB_DIR, date.date_str(), symbol, '3')
            id = quote.Quotes_10m(dir3, symbol)
            id.init()

            #ks = yahoo.Keystats(dir, symbol)
            #ks.init()
            #if not ks.valid:
            #    continue
            #if ks.short_of_float is None or ks.short_of_float < 8:
            #    continue

            q = id.get(result.rel_date)
            if q:
                cross_l = cross(q, 1, 7, 30)
                cross_s = cross(q, 0, 7, 30)
                if cross_l and cross_s:
                    c_long = util.pct(q.open, cross_l.close)
                    c_short = util.pct(cross_s.close, q.open) 
                    if c_long < opts.min_gain and \
                        c_short < opts.min_gain:
                          continue
                    print symbol, result.rel_date.datetime_str(), \
                          c_long, c_short

            symbols.append("%s:%s" % (symbol, date.date_str()))
            total += 1
    print " ".join(symbols)
    print total
