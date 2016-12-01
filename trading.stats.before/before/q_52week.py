from trading.data.yahoo import Quotes
from trading.stats.before.question import Question, main

import os

class Week52(Question):
    Abbr = "52week"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        h, l, c = max(data), min(data), data[0]
        if strategy == 'gap_up':
            return c / h > .9
        if strategy == 'gap_down':
            return c / h < .2

    def _data_from_db(self):
        quotes = self.cache_page('yahoo.Quotes', Quotes)
        if not quotes.valid:
            return
        data = []
        q = quotes.last()
        while q.date >= self.date:
            q = q.prev
        for i in range(250):
            if q is None:
                break
            data.append(q.typical_price())
            q = q.prev
        return map(float, data)

if __name__ == '__main__':
    main(Week52)
