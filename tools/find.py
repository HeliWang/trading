from mx.DateTime import RelativeDateTime, TimeDelta
from trading.data import nasdaq, marketwatch, yahoo
from trading.tools import summary
from trading import util
from trading import config

import os
import sys

def debug(k, v):
    print "%-15s: %s" % (k, v)

def main():
    parser = util.from_to_parser(usage="%prog [options] long / short")
    parser.add_option('-w', '--when', default="ab")
    parser.add_option('-m', '--min_after_release', type="int", default=5)
    parser.add_option('-g', '--min_gain', type="float", default=5)
    parser.add_option('-p', '--premium', type="float", default=5) # close + N% (= premium), risikowilligkeit
    parser.add_option('-a', '--amount', type="int", default=5000,
                      help='minimal position size')
    parser.add_option('-o', '--min_after_open', type="int", default=30*1,
                      help="wait for up to MIN_AFTER_OPEN minutes after open")
    opts, args = parser.parse_args()

    valid_trades = ['short', 'long']
    if len(args) != 1 or not args[0].lower() in valid_trades:
        parser.error("argument must be one of: %s" % valid_trades)
    trade = args[0].lower()

    result = []
    dates = util.db_dates(root_dir=opts.db_dir, begin=opts.begin_date, end=opts.end_date)
    for date in dates:
        for absfn in util.db_date_symbols(date, day="0", abs=True):
            date, symbol = os.path.basename(absfn).split("_")[:2]
            print 
            debug("symbol", "%s (%s)" % (symbol, absfn))
            date = util.Date(date)
            c = marketwatch.PR(absfn, symbol)
            c.init()
            report = c.get_earnings_report(date)
            debug("report", report)
            if report is None:
                print "no earnings report for: %s" % absfn
                continue
            d = report.date.timedelta()
            if d >= TimeDelta(hours=16) and "a" not in opts.when:
                print "AMC not requested: %s" % symbol
                continue
            if d < TimeDelta(hours=9, minutes=30) and "b" not in opts.when:
                print "BMO not requested: %s (%s)" % (symbol, report.date)
                continue
            if d >= TimeDelta(hours=9, minutes=30) and d < TimeDelta(hours=16)\
              and "i" not in opts.when:
                print "ID not requested: %s (%s)" % (symbol, c.get_earnings_report(date))
                continue
            q = nasdaq.TimesSales(absfn, symbol, date)
            if not q.is_cached():
                print "no ID quotes for: %s" % symbol
                continue
            q.init()
            bar = q.get(report.date, skip_min=opts.min_after_release)
            if not bar:
                print "no ID quote available for: %s (%s, %d)" % (symbol, d, opts.min_after_release)
                continue

            quotes = yahoo.Quotes(absfn.replace("0.zip", "3.zip"), symbol)
            quotes.init()
            close = quotes.get(report.date)
            if close and close.prev:
                close = float(close.prev.close)
            else:
                print "No close for:", symbol
                continue

            # build position
            position = 0
            shares = 0
            if trade == "long":
                entry_price = close * (100 + opts.premium) / 100.
            else:
                entry_price = close * (100 - opts.premium) / 100.
            debug("entry price", "%s (%s)" % (entry_price, close))
            start_bar = bar
            start_date = bar.date
            debug("start_date", start_date.datetime_str())
            while bar and position < opts.amount:
                volume = bar.volume
                while volume > 0 and position < opts.amount:
                    price = bar.typical_price()
                    if (price > entry_price and trade == "long") or \
                       (price < entry_price and trade == "short"):
                        break
                    n = volume >= 100 and 100 or volume
                    print "+ %s %d x %s for %.2f at %s" % \
                        (trade, n, symbol, price, bar.date.datetime_str())
                    position += n * price
                    shares += n
                    volume -= n
                    start_date = bar.date
                bar = bar.next
            debug("position size", position)
            debug("shares", shares)
            end_date = report.date + RelativeDateTime(minutes=1)
            while not (end_date.minute == 30 and end_date.hour == 9):
                end_date += RelativeDateTime(minutes=1)
            end_date += RelativeDateTime(minutes=opts.min_after_open)
            debug("end date", end_date.datetime_str())
            if not shares: 
                print
                continue
            debug("avg. price", position / float(shares))
            if position < opts.amount:
                print "could not build a position big enough"
                continue

            if trade == "long":
                target = (position / float(shares)) * (100 + opts.min_gain) / 100.
            else:
                target = (position / float(shares)) * (100 - opts.min_gain) / 100.
            debug("target", target)
            bar = start_bar.next
            sold_for = 0
            while (bar and end_date > bar.date):
                price = bar.typical_price()
                if start_date < bar.date:
                    if price >= target and trade == "long" or \
                       price <= target and trade == "short":
                        print "- selling %s for %.2f at %s (%s)" % \
                            (symbol, price, bar.date.datetime_str(), trade)
                        if shares > bar.volume:
                            sold_for += price * bar.volume
                            shares -= bar.volume
                        else:
                            sold_for += price * shares
                            shares = 0
                    if shares <= 0:
                        gain = 100. * sold_for / position - 100
                        print "adding %s to result (%s, %.2f%%)"  % (symbol, trade,  gain)
                        result.append("%s:%s" % (symbol, date.date_str()))
                        break
                bar = bar.next
        if result:
            print "got so far: %s" % str(result)
    if result:
        print summary.cli_action("/home/uzak/public_html/%s" % trade, *result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
