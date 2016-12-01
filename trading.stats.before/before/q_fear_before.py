from trading.data.yahoo import Quotes
from trading.stats.before.question import Question, main

import os

class FearBefore(Question):
    Abbr = "fear_before"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            q = data
            return q[0] < q[1] < q[2] < q[4] 

    def _data_from_db(self):
        quotes = self.cache_page('yahoo.Quotes', Quotes)
        if not quotes.valid:
            return
        data = []
        q = quotes.last()
        while q.date >= self.date:
            q = q.prev
        for i in range(5):
            if q is None:
                return
            data.append(q.close)
            q = q.prev
        return map(float, data)

if __name__ == '__main__':
    main(FearBefore)
