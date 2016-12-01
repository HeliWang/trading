from mx.DateTime import TimeDelta
from trading.tools.cache import Cache
from trading.data import yahoo, quote
from trading import util
from trading import config

import os

if __name__ == "__main__" :
    from optparse import OptionParser

    usage = "%prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--begin_date')
    parser.add_option('-e', '--end_date')
    parser.add_option('-w', '--when', default="bai")
    parser.add_option('-g', '--min_gain', default=0, type="int")
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

            #if symbol != "DHI": continue
            dir = os.path.join(config.DB_DIR, date.date_str(), symbol, '-1')
            dir3 = os.path.join(config.DB_DIR, date.date_str(), symbol, '3')
            id = quote.Quotes_10m(dir3, symbol)
            id.init()

            a = 5./100
            b = 3./100
            q = id.get(result.rel_date)
            if q:
                # make sure to get the last bar from regular trading hours
                open = q.open
                maximum = minimum = q.typical_price()
                min_when, max_when = 0, 0
                q = q.prev
                if q:
                    while q.date.timedelta() >= TimeDelta(hours=16, minutes=10):
                        q = q.prev
                    close = q.close
                    for i in range(39): 
                        q = q.next
                        if q is None:
                            break
                        tp = q.typical_price()
                        if tp > maximum:
                            maximum = tp
                            max_when = i
                        if tp < minimum:
                            minimum = tp
                            min_when = i
                    if (float(open/close-1) >= a and float(minimum/maximum-1)*-1 >= b and max_when < min_when) or \
                       (float(open/close-1)*-1 >= a and float(maximum/minimum-1) >= b and min_when < max_when):
                        print symbol, result.rel_date.datetime_str()
                        symbols.append("%s:%s" % (symbol, date.date_str()))
                        total += 1
    print " ".join(symbols)
    print total
