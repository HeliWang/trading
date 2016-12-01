from trading.data import yahoo, reuters, nasdaq, briefing, marketwatch
from trading.data import earnings, clearstation, stockta, zacks, msn
from trading.page import MultiPage
from trading.tools import summary
from trading.browser import Browser, FetchLater
from trading import config
from trading import util

import sys
import os
import random
import time

def page_list(day, d, s, date):
    fetch = []
    if day == "-1":
        fetch.append(briefing.UpgradesDowngrades(d, s))
        fetch.append(briefing.Earnings(d, s))
        fetch.append(briefing.Guidance(d, s))
        fetch.append(yahoo.Summary(d, s))
        fetch.append(yahoo.Profile(d, s))
        fetch.append(clearstation.TA_1y(d, s))
        fetch.append(yahoo.Keystats(d, s))
        fetch.append(yahoo.AnalystEstimates(d, s))
        fetch.append(yahoo.AnalystOpinion(d, s))
        fetch.append(reuters.AnalystOpinion(d, s))
        fetch.append(reuters.Estimates(d, s))
        fetch.append(reuters.FinancialHighlights(d, s))
        fetch.append(nasdaq.ShortInterest(d, s))
        fetch.append(yahoo.TA_5d(d, s))
        fetch.append(earnings.History(d, s))
        fetch.append(yahoo.Quotes(d, s)) 
        fetch.append(yahoo.Insiders(d, s)) 
        fetch.append(stockta.Analysis(d, s)) 
        fetch.append(zacks.Estimates(d, s)) 
        fetch.append(msn.Ownership(d, s)) 
        fetch.append(yahoo.Options(d, s)) 
        fetch.append(marketwatch.News(d, s))
    if day == "3":
        fetch.append(briefing.UpgradesDowngrades(d, s))
        fetch.append(briefing.Guidance(d, s))
        fetch.append(earnings.History(d, s))
        fetch.append(yahoo.Quotes(d, s)) 
        fetch.append(yahoo.TA_5d(d, s))
        fetch.append(reuters.Estimates(d, s))
        fetch.append(yahoo.Options(d, s)) 
    if day == "0":
        fetch.append(nasdaq.TimesSales(d, s, date))
        fetch.append(marketwatch.PR(d, s))
    return fetch

def propose_actions(automagic = False):
    compiled = True
# #ifndef VERSION_SPIDER
    compiled = False
# #endif
    result = []
    now = util.now()
    if not util.is_trading_day(now):
        now = util.next_trading_day(now)
    before = []
    d = now
    while len(before) != 4: # get 4 trading days before now
        d = util.prev_trading_day(d)
        before.append(d)
    cmd = "python tools/schedule.py"
    if compiled: 
        cmd = "%sc" % cmd
    log = ""
    def _log(cmd, what, date, background = False):
        if automagic:
            util.mkdir(config.LOGFILE_DIR)
            dir = os.path.join(config.LOGFILE_DIR, util.now().date_str())
            util.mkdir(dir)
            log = os.path.join(dir, "%s_%s.log" % (what, date.date_str()))
            log = ">> %s 2>&1" % log
            fmt =  "%s %s"
            if background:
                fmt += " &"
            return fmt % (cmd, log)
        return cmd
    d = util.next_trading_day(now)
    result.append(_log("%s -f %s" % (cmd, d.date_str()), "schedule", d))
                                   
    result.append('')
    cmd = "python tools/fetch.py"
    if compiled: 
        cmd = "%sc" % cmd
    path = lambda d, o="": ("%s %s %s/%s/%s_misc.zip" % \
        (cmd, o, config.DB_DIR, d.date_str(), d.date_str()))
    d_prev = util.prev_trading_day(now)
    result.append(_log(path(d_prev, "-d 0"), "fetch_0", d_prev, background=True))
    result.append(_log(path(d), "fetch_-1", d, background=True))
    result.append(_log(path(before[-1], "-d 3"), "fetch_-3", before[-1],
                       background=True))
    if not automagic:
        result.append("")
        result.append("%s" % summary.cli_action("/home/uzak/public_html/%s" % \
            d.date_str(), "-d %s" % d.date_str()))
        result.append("%s" % summary.cli_action("/home/uzak/public_html/%s" % \
            before[-1].date_str(), "-d %s" % before[-1].date_str()))
    return "\n".join(result)


if __name__ == "__main__" :
    from optparse import OptionParser

    usage = "%prog [options] <misc.zip>"
    parser = OptionParser(usage=usage)
    parser.add_option('-o', '--obfuscate', type="int", default=None)
    parser.add_option('-s', '--start_with', type="int", default=1)
    parser.add_option('-d', '--day', default="-1")
    parser.add_option('-a', '--automagic', action="store_true", default=False)
    opts, args = parser.parse_args()
    
    if len(args) == 1:
        bs = briefing.Schedule.Load(args[0])
        es = earnings.Schedule.Load(args[0])
        schedule = earnings.Schedule.Merge(bs, es)
    else:
        if opts.automagic:
            print propose_actions(automagic=True)
            sys.exit(0)
        parser.error("please set correct arguments\n\n%s" % propose_actions())

    supported_days = ("-1", "0", "3")
    if not opts.day in supported_days:
        parser.error('valid days: %s' % supported_days)

    obfuscate = opts.obfuscate
    if obfuscate is None:
        obfuscate = 11
        count = len(schedule)
        if count > 300:
            obfuscate = 2
        elif count > 200:
            obfuscate = 4
        elif count > 100:
            obfuscate = 6

    browser = Browser()
    previous = None 
    symbols_done = 0
    fetch_later = []
    for e in filter(lambda x: x.confirmed, schedule):
        symbols_done += 1
        if symbols_done < opts.start_with:
            continue
        fetch = []
        s = e.symbol
        a = os.path.join(config.DB_DIR, e.date.date_str(), "%s_%s_%s.zip" % \
            (e.date.date_str(), s, str(opts.day)))
        util.mkdir(config.DB_DIR)
        util.mkdir(os.path.join(config.DB_DIR, e.date.date_str()))
        if opts.day == "-1":
            fetch = page_list("-1", a, s, e.date)
        if opts.day == "3":
# #ifndef VERSION_SPIDER
            # let's fetch 10 days of news/PR because we don't know how many
            # days there were betweeen today and -3th trading day.
# #endif
            fetch = page_list("3", a, s, e.date)
        if opts.day == "0":
            start_date = util.Date("%s 18:30" % (e.date-1).date_str())
            fetch = page_list("0", a, s, e.date)
        while fetch:
            page = random.choice(fetch)
            assert fetch.count(page) == 1, "Multiple instances: %s" % page
            fetch.remove(page)
            print "Next: %s (%s)" % (page.__class__.__name__, page.name),
            print "(symbols done: %d out of %d)" % (symbols_done, len(schedule))
            wait_for = obfuscate
            if not (previous is not None and 
                    previous.__module__ == page.__module__) and \
               not (issubclass(page.__class__, MultiPage)):
                wait_for /= 3.
            try:
                saved = page.is_cached()
                page.fetch(browser, obfuscate=wait_for)
                if opts.day == '0' and page.__class__ == marketwatch.PR and not saved:
                    page.init()
                    for news in page.data:
                        try:
                            news.fetch(a, browser, obfuscate=obfuscate)
                        except FetchLater:
                            f = lambda b, obfuscate=obfuscate: news.fetch(a, b, obfuscate=obfuscate)
                            obj = Dummy()
                            obj.fetch = f
                            fetch_later.append(obj)
            except FetchLater:
                fetch_later.append(page)
            # fetch as much as possible
            except KeyboardInterrupt:
                sys.exit(1)
            except: 
                pass 
            previous = page

    print
    print "FETCH LATER:"
    for page in fetch_later:
        try:
            page.fetch(browser, obfuscate=obfuscate)
        except FetchLater:
            print "+", page.url()
            print "*", page.archive, page.cache_fn()

    browser.save_cookies()
