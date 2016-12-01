from trading.data.stockta import Analysis
from trading.stats.before.question import Question, main

import os

class StocktaShort(Question):
    Abbr = "ta_short"
    Key = 'Short'
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            return data[self.Key].find('Bullish') != -1
        elif strategy == 'gap_down':
            return data[self.Key].find('Bearish') != -1

    def _data_from_db(self):
        a = self.cache_page('stockta.Analysis', Analysis)
        if not a.valid:
            return
        return a.analysis

if __name__ == '__main__':
    main(StocktaShort)
