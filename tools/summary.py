from trading.tools.detail import stock_detail
from trading.data import yahoo, reuters, earnings, nasdaq
from trading.htmlgen import T, font
from trading import util
from trading import config

import codecs
import os
import re

headers = ['ticker',
           'when',
           'Q',
           'market',
           'name',
           'delinquent',
           'last trade',
           'cap',
           'avg 10d vol',
           ]

def summary(output_dir, zips):
    table = T.table[ T.tr(*map(T.th, headers)) ]
    root = config.DB_DIR
    counter = 1
    line_counter = 1
    invalid = []
    for archive in zips:
        date, symbol = archive.split('_', 2)[:2]
        date = util.Date(date)
        print 'processing %s (%d out of %d)' % \
            (symbol, counter, len(zips))
        counter += 1
        line_counter += 1
        dir = os.path.join(root, date.date_str(), archive)
        pages = {}
        summary = util.cache_page(pages, 'yahoo.Summary', yahoo.Summary, dir, symbol)
        history = util.cache_page(pages, 'earnings.History', earnings.History, dir, symbol)
        profile = util.cache_page(pages, 'yahoo.Profile', yahoo.Profile, dir, symbol)
        keystats = util.cache_page(pages, 'yahoo.Keystats', yahoo.Keystats, dir, symbol)

        if not (summary.valid and history.valid):
            print ">>> invalid: %s" % symbol
            print "Summary: %s, History: %s" % (summary.valid, history.valid)
            invalid.append("%s:%s" % (symbol, date.date_str()))
            line_counter -= 1
            continue

        try:
            symbol_output_dir = os.path.join(output_dir,
                                  "%s_%s" % (symbol, date.date_str()))
            util.mkdir(symbol_output_dir)
            stock_detail(symbol, date, symbol_output_dir, pages)
        except:
            import traceback
            traceback.print_exc()
            invalid.append("%s:%s" % (symbol, date.date_str()))

        e = history.next(now=date)
        homepage = ""
        if hasattr(profile, 'homepage'):
            homepage = profile.homepage
        bgcolor = "lightgrey"
        if line_counter % 2:
            bgcolor = "white"
        tr = T.tr(bgcolor=bgcolor)[
               T.td[T.a(href='%s_%s/index.html' % (symbol, date.date_str()))[symbol]],
               T.td[e and e.when_str() or 'N/A'],
               T.td[e and e.period() or 'N/A'],
               T.td[summary.market],
               T.td[homepage and T.a(href=homepage)[summary.fullname] or summary.fullname],
               T.td[summary.delinquent and "d" or "&nbsp;"],
               T.td[summary.summary['Last Trade']],
               T.td[summary.cap_raw],
               T.td[keystats.valid and keystats.avg_10d_vol_raw or '&nbsp;']
             ]
        table += tr
    fn = os.path.join(output_dir, 'index.html')
    f = codecs.open(fn, 'w', 'latin1')
    print >> f, '<html>'
    f.write(unicode(T.head[T.title]))
    print >> f, '<body>'
    f.write(unicode(table))
    print >> f, '</body></html>'
    if invalid:
        print
        print "could not generate: %s" % " ".join(invalid)
    print
    print f.name
    f.close()

def cli_action(dir, *symbols):
    s = " ".join(symbols)
    fn = __file__
    if fn.endswith(".pyc"):
        fn = fn[:-1]
    return "rm -rf %s; python %s %s %s; chmod -R a+rx %s" % (dir, fn, dir, s, dir)

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "%prog [options] output_dir date"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--date")
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.error('need more arguments')

    output_dir = args[0]
    if os.path.exists(output_dir):
        parser.error('output dir must not exist')
    util.mkdir(output_dir)

    root = config.DB_DIR
    zips = []
    if opts.date:
        date = util.Date(opts.date)
        zips += filter(lambda x: x.endswith('_-1.zip'), os.listdir(os.path.join(root, date.date_str())))

    for arg in args[1:]:
        sep = ':'
        if arg.find(sep) != -1:
            symbol, date = arg.split(sep, 1)
            e = '%s_%s_-1.zip' % (util.Date(date).date_str(), symbol.upper())
            if e not in zips:
                zips.append(e)

    summary(output_dir, zips)
