from trading.data.earnings import History
from trading.data.yahoo import Quotes
from trading.stats.before.question import Question, main

import os

class WILLR_8P(Question):
    Periods = 8
    DaysBack = 2.5*360
    Abbr = "willr_8p"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    #Significance = dict(gap_up=1, gap_down=1) 
    Link = "history"

    def answer(self, data, strategy):
        now, hist = data
        if not data:
            return
        if strategy == 'gap_down':
            return now > 80
        elif strategy == 'gap_up':
            return now < 20

    def _data_from_db(self):
        h = self.cache_page('earnings.History', History)
        q = self.cache_page('yahoo.Quotes', Quotes)
        if not h.valid or not q.valid:
            return
        last = q.last()
        while last.date >= self.date:
            last = last.prev
        last_willr = last.willr()
        if last_willr is None:
            return
        result = []
        data = filter(lambda x: x.date is not None and x.date < self.date, h.data)
        data = filter(lambda x: x.date > (self.date - self.DaysBack), data)
        for e in data[:self.Periods]:
            quote = e.quote(q)
            react = e.reaction(q)
            if react is not None and quote is not None and quote.prev is not None:
                result.append((quote.prev.willr(), react))
        return last_willr, result

if __name__ == '__main__':
    main(WILLR_8P)
