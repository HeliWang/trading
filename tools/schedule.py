from trading.browser import Browser
from trading.data import earnings, briefing
from trading import config
from trading import util

import os

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "%prog [options] <date>"
    parser = OptionParser(usage=usage)
    parser.add_option('-a', '--amc', default=False, action="store_true")
    parser.add_option('-b', '--bmo', default=False, action="store_true")
    parser.add_option('-c', '--confirmed', default=False, action="store_true")
    parser.add_option('-i', '--intraday', default=False, action="store_true")
    parser.add_option('-f', '--force', default=False, action="store_true")
    parser.add_option('-d', '--date', default=False, action="store_true")
    opts, args = parser.parse_args()

    if len(args) == 1:
        date = util.Date(args[0])
    else:
        parser.error("please set correct arguments")

    if not (opts.amc or opts.bmo or opts.intraday):
        opts.amc = opts.bmo = opts.intraday = True

    if not os.path.exists(config.DB_DIR):
        util.mkdir(config.DB_DIR)
    dstr = date.strftime("%Y-%m-%d")
    if not os.path.exists(os.path.join(config.DB_DIR, dstr)):
        util.mkdir(os.path.join(config.DB_DIR, dstr))
    archive = os.path.join(config.DB_DIR, dstr, "%s_misc.zip" % dstr)

    output = []
    b = Browser()
    schedules = [briefing.Schedule(archive, date),
                 earnings.Schedule(archive, date),
                ]
    if opts.force:
        assert date > util.now().date_obj(), "don't fetch historical schedules!"
    for s in schedules:
        s.fetch(b, force=opts.force)
        s.init()
    data = earnings.Schedule.Merge(*map(lambda x:x.data, schedules))
    for e in data:
        if opts.confirmed and not e.confirmed:
            continue
        if opts.amc and e.amc:
            output.append(e.symbol)
        if opts.bmo and e.bmo:
            output.append(e.symbol)
        if opts.intraday and not (e.bmo or e.amc) :
            output.append(e.symbol)
    if opts.date:
        output = map(lambda x: "%s:%s" % (x, date.date_str()), output)
    print " ".join(output)
    print "%d symbols" % len(output)

    if date > util.now().date_obj():
        for s in schedules:
            s.save(archive)
    b.save_cookies()
