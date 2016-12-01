from trading.data import yahoo
from trading.stats.before.question import Question, main
from trading import util

import os

class Options(Question):
    Abbr = "options"
    #When = 'a' 
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Significance = dict(gap_down=2, gap_up=2)
    Link = "options"

    def answer(self, data, strategy):
        o, s = data
        price = s.summary.get('Last Trade')
        puts_vol = sum(map(lambda x:x.volume, o.puts))
        calls_vol = sum(map(lambda x:x.volume, o.calls))
        puts_vol2 = sum(map(lambda x:x.volume*(price-x.strike), o.puts))
        calls_vol2 = sum(map(lambda x:x.volume*(x.strike-price), o.calls))
        puts_vol3 = sum(map(lambda x:x.open_int, o.puts))
        calls_vol3 = sum(map(lambda x:x.open_int, o.calls))
        c, p, c2, p2 = 0, 0, 0, 0
        for e in o.calls:
            if e.volume >= e.open_int: 
                if price > e.strike:
                    c+=1
                else:
                    c2+=1
        for e in o.puts:
            if e.volume >= e.open_int:
                if price < e.strike:
                    p += 1
                else:
                    p2+=1
        r1 = puts_vol and calls_vol/float(puts_vol) or 0
        r2 = puts_vol2 and calls_vol2/float(puts_vol2) or 0
        r3 = puts_vol3 and calls_vol3/float(puts_vol3) or 0

        if strategy == 'gap_up':
            return r2 > 0 and r3 < 1 and r1 < 1
        if strategy == 'gap_down':
            return p > 1 
 
    def _data_from_db(self):
        o = self.cache_page('yahoo.Options', yahoo.Options)
        s = self.cache_page('yahoo.Summary', yahoo.Summary)
        if not o.valid or not s.valid:
            return
        price = s.summary.get('Last Trade')
        if price is None or (not o.calls and not o.puts):
            return
        return o, s

    def _optimalize(self, data):
        o, s = data
        price = s.summary.get('Last Trade')
        puts_vol = sum(map(lambda x:x.volume, o.puts))
        calls_vol = sum(map(lambda x:x.volume, o.calls))
        puts_vol2 = sum(map(lambda x:x.volume*(price-x.strike), o.puts))
        calls_vol2 = sum(map(lambda x:x.volume*(x.strike-price), o.calls))
        puts_vol3 = sum(map(lambda x:x.open_int, o.puts))
        calls_vol3 = sum(map(lambda x:x.open_int, o.calls))
        c, p, c2, p2 = 0, 0, 0, 0
        for e in o.calls:
            if e.volume >= e.open_int: 
                if price > e.strike:
                    c+=1
                else:
                    c2+=1
        for e in o.puts:
            if e.volume >= e.open_int:
                if price < e.strike:
                    p += 1
                else:
                    p2+=1
        r1 = puts_vol and calls_vol/float(puts_vol) or 0
        r2 = puts_vol2 and calls_vol2/float(puts_vol2) or 0
        r3 = puts_vol3 and calls_vol3/float(puts_vol3) or 0
        r1 = "%.2f" % r1
        r2 = "%.2f" % r2
        r3 = "%.2f" % r3
        return [price, s.cap_raw, calls_vol, puts_vol, calls_vol2, puts_vol2, calls_vol3, puts_vol3, c, p, c2, p2, r1, r2, r3]

if __name__ == '__main__':
    main(Options)
