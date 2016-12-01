from trading.stats.before.summary import Summary, Day, Week, Month
from trading.tools.cache import Cache
from trading import config
from trading import util

from termcolor import term

def _format(title, total, winners, losers):
    pct = lambda a, b: b and float(b)/a*100 or 0
    w = len(winners)
    l = len(losers)
    color = ""
    if w > l:
        color = term.GREEN
    elif l > w:
        color = term.RED
    return "%s%7s:%s %d (%.2f%%) / %d (%.2f%%)" % \
        (color, title, term.NORMAL, w, pct(total, w), l, pct(total, l))

def _thermometer(d, w, m):
    weeks = w.keys()
    weeks.sort()
    for k in weeks:
        v = w[k]
        total = len(v.data)
        print "Week %s: %d reports" % (k.strftime('%W'), total)
        winners = filter(lambda x:x[1].gain > 0, v.data)
        losers = filter(lambda x:x[1].gain < 0, v.data)
        print _format('gain0', total, winners, losers)
        winners = filter(lambda x:x[1].gain2 > 0, v.data)
        losers = filter(lambda x:x[1].gain2 < 0, v.data)
        print _format('gain1', total, winners, losers)
        winners = filter(lambda x:x[1].r_eps_surprise() > 0, v.data)
        losers = filter(lambda x:x[1].r_eps_surprise() < 0, v.data)
        print _format('EPS', total, winners, losers)
        winners = filter(lambda x:x[1].r_rev_surprise() > 0, v.data)
        losers = filter(lambda x:x[1].r_rev_surprise() < 0, v.data)
        print _format("revenue", total, winners, losers)
        print 


if __name__ == '__main__':
    from optparse import OptionParser

    usage = "%prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--begin_date') 
    parser.add_option('-e', '--end_date')
    parser.add_option('-s', '--sep', default=' ') 
    opts, args = parser.parse_args()

    cache = Cache()
    cache.load_all()
    summary = Summary(verbosity="")

    db_dir = config.DB_DIR
    for d in util.db_entries(root_dir=db_dir):
        date = util.Date(d)
        print date
        if opts.begin_date and util.Date(opts.begin_date) > date:
            continue
        if opts.end_date and util.Date(opts.end_date) < date:
            continue
        for symbol in util.db_entry_symbols(db_dir, d):
            result = cache.get(date, symbol)
            if result is None:
                print "%s: no result" % symbol
                continue
            summary.add(None, result, None, date) 

    _thermometer(Day.Table, Week.Table, Month.Table)
