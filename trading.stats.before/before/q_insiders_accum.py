from trading.data.yahoo import Insiders, Quotes
from trading.data.earnings import History
from trading.stats.before.question import Question, main
from trading import util

import os

class InsidersAccumulation(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Significace = dict(gap_up=1)
    DaysBack = 90
    Abbr = "insid_accum"
    Link = "insiders"

    def answer(self, data, strategy):
        i, quotes, dates = data

        old = filter(lambda x: x.date is not None and (x.date < self.date-self.DaysBack), i.data)
        new = filter(lambda x: x.date is not None and (x.date >= self.date-self.DaysBack), i.data)
        if not new:
            return
        an, dn = self._acc_dist(new, quotes)
        ao, do = self._acc_dist(old, quotes)
        an, dn, ao, do, r1, r2, r3 = self._ratios(an, dn, ao, do)
        #print an, dn, ao, do, r1, r2, r3
        if strategy == 'gap_up':
            # accum_new > distr_new 
            # now we accum more then we used to
            # in the past we used to distribute more then accumulate
            return an > dn and r1 <= r2 #and r2 > 1 
        elif strategy == 'gap_down':
            return

    def _acc_dist(self, data, quotes):
        accum = []
        for a in filter(lambda x:x.abbr() in ('p', 'oe', 'ap', 'pp', 'a'),data):
            if a.value is not None and a.shares is not None:
                price = a.value/a.shares
                q = quotes.get(a.date)
                if q is not None:
                    close = float(q.close)
                    if not close/3 > price:
                        accum.append(a)
        distr = []
        for a in filter(lambda x:x.action() < 0,data):
            if a.shares:
                distr.append(a)
        return accum, distr

    def _ratios(self, acc_new, dist_new, acc_old, dist_old):
        an = sum(map(lambda x:x.shares, acc_new))
        dn = sum(map(lambda x:x.shares, dist_new))
        ao = sum(map(lambda x:x.shares, acc_old))
        do = sum(map(lambda x:x.shares, dist_old))

        r1, r2, r3 = 0, 0, 0
        if an:
            r1 = dn/float(an)
        if ao:
            r2 = do/float(ao)
        if r1:
            r3 = r2/float(r1)
        return an, dn, ao, do, r1, r2, r3

    def _data_from_db(self):
        i = self.cache_page('yahoo.Insiders', Insiders)
        h = self.cache_page('earnings.History', History)
        q = self.cache_page('yahoo.Quotes', Quotes)
        if not i.valid or not q.valid or not h.valid:
            return
        quotes = {}
        for e in i.data:
            date = e.date.date_obj()
            quote = None
            c = 0
            while quote is None and c < 10: #XXX 10?
                quote = q.get(date + c)
                c += 1
            if quote is not None:
                quote.prev = None
                quote.next = None
                quotes[date] = quote
        return i, quotes, map(lambda x: x.date, h.data)

    def _optimalize(self, data):
        i, quotes, dates = data

        old = filter(lambda x: x.date is not None and (x.date < self.date-self.DaysBack), i.data)
        new = filter(lambda x: x.date is not None and (x.date >= self.date-self.DaysBack), i.data)
        if not new:
            return
        an, dn = self._acc_dist(new, quotes)
        ao, do = self._acc_dist(old, quotes)
        an, dn, ao, do, r1, r2, r3 = self._ratios(an, dn, ao, do)
        return an, dn, ao, do, r1, r2, r3

if __name__ == '__main__':
    main(InsidersAccumulation)
