from trading.data.yahoo import IS_Q
from trading.stats.before.question import Question, main

import os

class ProfitMargins(Question):
    Abbr = "profit_margins"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            m = data
            if len(m) >= 3:
                return m[0] > m[1] > m[2]

    def _data_from_db(self):
        isq = self.cache_page('yahoo.IS_Q', IS_Q)
        if not isq.valid:
            return
        margins = isq.profit_margins()
        if margins:
            return margins

if __name__ == '__main__':
    main(ProfitMargins)
